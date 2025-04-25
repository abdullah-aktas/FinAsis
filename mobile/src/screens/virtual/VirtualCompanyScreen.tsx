import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Button, Text, List } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';

const VirtualCompanyScreen = () => {
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
          <Title>Sanal Şirket İşlemleri</Title>
          <View style={styles.buttonContainer}>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('CompanyList')}
            >
              Şirketler
            </Button>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('Simulation')}
            >
              Simülasyon
            </Button>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Şirket Performansı</Title>
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
          <Title>Aktif Şirketler</Title>
          <List.Item
            title="ABC Yazılım A.Ş."
            description="Yazılım Geliştirme"
            left={props => <List.Icon {...props} icon="office-building" />}
            right={props => <Text style={styles.companyStatus}>Aktif</Text>}
          />
          <List.Item
            title="XYZ Danışmanlık"
            description="İş Danışmanlığı"
            left={props => <List.Icon {...props} icon="office-building" />}
            right={props => <Text style={styles.companyStatus}>Aktif</Text>}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Son İşlemler</Title>
          <List.Item
            title="Yeni Şirket Kurulumu"
            description="ABC Yazılım A.Ş. - 25.03.2024"
            left={props => <List.Icon {...props} icon="plus" color="green" />}
            right={props => <Text>Tamamlandı</Text>}
          />
          <List.Item
            title="Simülasyon Başlatıldı"
            description="XYZ Danışmanlık - 24.03.2024"
            left={props => <List.Icon {...props} icon="play" color="blue" />}
            right={props => <Text>Devam Ediyor</Text>}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Şirket Raporları</Title>
          <Button mode="outlined" style={styles.reportButton}>
            Finansal Performans Raporu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Operasyonel Rapor
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Simülasyon Sonuçları
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
  companyStatus: {
    color: 'green',
    fontWeight: 'bold',
  },
  reportButton: {
    marginBottom: 10,
  },
});

export default VirtualCompanyScreen; 