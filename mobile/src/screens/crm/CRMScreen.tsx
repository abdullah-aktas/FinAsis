import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Button, Text, Avatar } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';

const CRMScreen = () => {
  const navigation = useNavigation();
  const screenWidth = Dimensions.get('window').width;

  const data = {
    labels: ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran'],
    datasets: [
      {
        data: [30, 45, 28, 80, 99, 43],
        color: (opacity = 1) => `rgba(134, 65, 244, ${opacity})`,
        strokeWidth: 2
      }
    ],
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Müşteri İlişkileri Yönetimi</Title>
          <View style={styles.buttonContainer}>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('Customers')}
            >
              Müşteriler
            </Button>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('Opportunities')}
            >
              Fırsatlar
            </Button>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Müşteri Takibi</Title>
          <View style={styles.customerItem}>
            <Avatar.Text size={40} label="AK" />
            <View style={styles.customerInfo}>
              <Text style={styles.customerName}>Ahmet Kaya</Text>
              <Text style={styles.customerStatus}>Aktif Müşteri</Text>
            </View>
            <Text style={styles.customerValue}>25,000 ₺</Text>
          </View>
          <View style={styles.customerItem}>
            <Avatar.Text size={40} label="MA" />
            <View style={styles.customerInfo}>
              <Text style={styles.customerName}>Mehmet Arslan</Text>
              <Text style={styles.customerStatus}>Potansiyel Müşteri</Text>
            </View>
            <Text style={styles.customerValue}>15,000 ₺</Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Satış Grafiği</Title>
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
          <Title>Fırsatlar</Title>
          <View style={styles.opportunityItem}>
            <Text>Yeni Proje Teklifi</Text>
            <Text style={styles.opportunityValue}>50,000 ₺</Text>
          </View>
          <View style={styles.opportunityItem}>
            <Text>Yazılım Güncelleme</Text>
            <Text style={styles.opportunityValue}>15,000 ₺</Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>CRM Raporları</Title>
          <Button mode="outlined" style={styles.reportButton}>
            Müşteri Analizi
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Satış Performansı
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Müşteri Memnuniyeti
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
  customerItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  customerInfo: {
    flex: 1,
    marginLeft: 10,
  },
  customerName: {
    fontWeight: 'bold',
  },
  customerStatus: {
    color: 'gray',
    fontSize: 12,
  },
  customerValue: {
    fontWeight: 'bold',
    color: 'green',
  },
  opportunityItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  opportunityValue: {
    fontWeight: 'bold',
    color: 'blue',
  },
  reportButton: {
    marginBottom: 10,
  },
});

export default CRMScreen; 