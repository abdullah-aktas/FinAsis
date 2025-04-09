import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';

const HomeScreen = ({ navigation }) => {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>FinAsis</Text>
        <Text style={styles.headerSubtitle}>Finansal Okuryazarlık Platformu</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Son Dersler</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {/* Ders kartları buraya gelecek */}
        </ScrollView>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Popüler Oyunlar</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {/* Oyun kartları buraya gelecek */}
        </ScrollView>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>İlerleme Durumu</Text>
        <View style={styles.progressContainer}>
          {/* İlerleme bilgileri buraya gelecek */}
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    padding: 20,
    backgroundColor: '#2196F3',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#fff',
    marginTop: 5,
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  progressContainer: {
    backgroundColor: '#f5f5f5',
    padding: 15,
    borderRadius: 10,
  },
});

export default HomeScreen; 