# -*- coding: utf-8 -*-
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from decouple import config
from typing import List, Dict, Any
import sys
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class IndexInfo:
    table_name: str
    index_name: str
    index_type: str
    column_name: str

class IndexChecker:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="finasis",
            user="postgres",
            password="postgres",
            host="localhost",
            port=5432,
            client_encoding='utf8'
        )
        self.conn.autocommit = True

    def get_existing_indexes(self) -> List[IndexInfo]:
        """Mevcut indeksleri getirir"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT
                t.relname as table_name,
                i.relname as index_name,
                CASE
                    WHEN ix.indisprimary THEN 'PRIMARY KEY'
                    WHEN ix.indisunique THEN 'UNIQUE'
                    ELSE 'INDEX'
                END as index_type,
                a.attname as column_name
            FROM
                pg_class t,
                pg_class i,
                pg_index ix,
                pg_attribute a
            WHERE
                t.oid = ix.indrelid
                AND i.oid = ix.indexrelid
                AND a.attrelid = t.oid
                AND a.attnum = ANY(ix.indkey)
                AND t.relkind = 'r'
                AND t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            ORDER BY
                t.relname,
                i.relname;
        """)
        return [IndexInfo(*row) for row in cur.fetchall()]

    def get_index_usage_stats(self) -> Dict[str, Dict[str, Any]]:
        """İndeks kullanım istatistiklerini getirir"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT
                schemaname || '.' || relname as table_name,
                idx_scan as index_scans,
                seq_scan as seq_scans,
                n_live_tup as live_tuples
            FROM
                pg_stat_user_tables
            WHERE
                schemaname = 'public';
        """)
        stats = {}
        for row in cur.fetchall():
            table_name, idx_scan, seq_scan, live_tuples = row
            total_scans = idx_scan + seq_scan
            index_usage_ratio = idx_scan / total_scans if total_scans > 0 else 0
            stats[table_name] = {
                'index_scans': idx_scan,
                'seq_scans': seq_scan,
                'live_tuples': live_tuples,
                'index_usage_ratio': index_usage_ratio
            }
        return stats

    def analyze_indexes(self):
        """İndeksleri analiz eder ve raporlar"""
        indexes = self.get_existing_indexes()
        stats = self.get_index_usage_stats()

        # Tablolara göre indeksleri grupla
        table_indexes = defaultdict(list)
        for idx in indexes:
            table_indexes[idx.table_name].append(idx)

        print("\n=== İndeks Analizi ===")
        for table_name, table_stats in stats.items():
            print(f"\nTablo: {table_name}")
            print(f"Toplam kayıt: {table_stats['live_tuples']}")
            print(f"İndeks taramaları: {table_stats['index_scans']}")
            print(f"Sıralı taramalar: {table_stats['seq_scans']}")
            print(f"İndeks kullanım oranı: {table_stats['index_usage_ratio']:.2%}")

            if table_name in table_indexes:
                print("\nMevcut indeksler:")
                for idx in table_indexes[table_name]:
                    print(f"  - {idx.index_name} ({idx.index_type}): {idx.column_name}")

            # Performans uyarıları
            if table_stats['seq_scans'] > table_stats['index_scans']:
                print("\n⚠️ UYARI: Sıralı taramalar indeks taramalarından fazla!")
            if table_stats['index_usage_ratio'] < 0.5:
                print("\n⚠️ UYARI: Düşük indeks kullanım oranı!")

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    checker = IndexChecker()
    checker.analyze_indexes()

if __name__ == "__main__":
    main() 