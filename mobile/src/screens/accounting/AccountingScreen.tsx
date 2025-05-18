import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Button, Text } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';

const AccountingScreen = () => {
  const navigation = useNavigation();

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Muhasebe İşlemleri</Title>
          <View style={styles.buttonContainer}>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('ChartOfAccounts')}
            >
              Hesap Planı
            </Button>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('Invoice')}
            >
              Fatura Oluştur
            </Button>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Son İşlemler</Title>
          <View style={styles.transactionItem}>
            <Text>#INV-2024-001</Text>
            <Text style={styles.amount}>1,250.00 ₺</Text>
          </View>
          <View style={styles.transactionItem}>
            <Text>#INV-2024-002</Text>
            <Text style={styles.amount}>3,450.00 ₺</Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Muhasebe Raporları</Title>
          <Button mode="outlined" style={styles.reportButton}>
            Bilanço
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Gelir Tablosu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Mizan
          </Button>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Özet</Title>
          <View style={styles.summaryItem}>
            <Text>Aylık Toplam Gelir</Text>
            <Text style={styles.income}>25,000.00 ₺</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text>Aylık Toplam Gider</Text>
            <Text style={styles.expense}>15,000.00 ₺</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text>Net Kar/Zarar</Text>
            <Text style={styles.profit}>10,000.00 ₺</Text>
          </View>
        </Card.Content>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
    backgroundColor: '#f5f5f5',
  },
  card: {
    marginBottom: 10,
    elevation: 4,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 10,
  },
  button: {
    marginHorizontal: 5,
  },
  reportButton: {
    marginBottom: 10,
  },
  transactionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  amount: {
    fontWeight: 'bold',
  },
  summaryItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  income: {
    color: 'green',
    fontWeight: 'bold',
  },
  expense: {
    color: 'red',
    fontWeight: 'bold',
  },
  profit: {
    color: 'blue',
    fontWeight: 'bold',
  },
});

export default AccountingScreen; 