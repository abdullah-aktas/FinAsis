import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Button, Text } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';

const FinanceScreen = () => {
  const navigation = useNavigation();
  const screenWidth = Dimensions.get('window').width;

  const data = {
    labels: ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran'],
    datasets: [
      {
        data: [20, 45, 28, 80, 99, 43],
        color: (opacity = 1) => `rgba(134, 65, 244, ${opacity})`,
        strokeWidth: 2
      }
    ],
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Finans İşlemleri</Title>
          <View style={styles.buttonContainer}>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('BankTransactions')}
            >
              Banka İşlemleri
            </Button>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('CashFlow')}
            >
              Nakit Akışı
            </Button>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Nakit Akışı Grafiği</Title>
          <LineChart
            data={data}
            width={screenWidth - 40}
            height={220}
            chartConfig={{
              backgroundColor: '#ffffff',
              backgroundGradientFrom: '#ffffff',
              backgroundGradientTo: '#ffffff',
              decimalPlaces: 0,
              color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
              style: {
                borderRadius: 16
              }
            }}
            bezier
            style={styles.chart}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Son İşlemler</Title>
          <View style={styles.transactionItem}>
            <Text>Banka Transferi</Text>
            <Text style={styles.amount}>-5,000.00 ₺</Text>
          </View>
          <View style={styles.transactionItem}>
            <Text>Müşteri Ödemesi</Text>
            <Text style={styles.amount}>+10,000.00 ₺</Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Hesap Özetleri</Title>
          <View style={styles.summaryItem}>
            <Text>Ana Hesap</Text>
            <Text style={styles.balance}>25,000.00 ₺</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text>Yatırım Hesabı</Text>
            <Text style={styles.balance}>50,000.00 ₺</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text>Toplam Varlıklar</Text>
            <Text style={styles.total}>75,000.00 ₺</Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Finansal Raporlar</Title>
          <Button mode="outlined" style={styles.reportButton}>
            Nakit Akışı Raporu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Bütçe Raporu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Yatırım Raporu
          </Button>
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
  chart: {
    marginVertical: 8,
    borderRadius: 16,
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
  balance: {
    color: 'green',
    fontWeight: 'bold',
  },
  total: {
    color: 'blue',
    fontWeight: 'bold',
    fontSize: 16,
  },
  reportButton: {
    marginBottom: 10,
  },
});

export default FinanceScreen; 