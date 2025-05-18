import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Button, Text, List } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { BarChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';

const InventoryScreen = () => {
  const navigation = useNavigation();
  const screenWidth = Dimensions.get('window').width;

  const data = {
    labels: ['Ürün A', 'Ürün B', 'Ürün C', 'Ürün D', 'Ürün E'],
    datasets: [{
      data: [20, 45, 28, 80, 99]
    }]
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Stok İşlemleri</Title>
          <View style={styles.buttonContainer}>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('Products')}
            >
              Ürünler
            </Button>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('StockCount')}
            >
              Stok Sayımı
            </Button>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Stok Durumu</Title>
          <List.Item
            title="Ürün A"
            description="Kritik Stok Seviyesi"
            left={props => <List.Icon {...props} icon="alert" color="red" />}
            right={props => <Text style={styles.stockLevel}>5 adet</Text>}
          />
          <List.Item
            title="Ürün B"
            description="Normal Stok Seviyesi"
            left={props => <List.Icon {...props} icon="check" color="green" />}
            right={props => <Text style={styles.stockLevel}>25 adet</Text>}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Stok Hareketleri</Title>
          <BarChart
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
            style={styles.chart}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Son Hareketler</Title>
          <List.Item
            title="Ürün A Giriş"
            description="25.03.2024"
            left={props => <List.Icon {...props} icon="arrow-down" color="green" />}
            right={props => <Text>+50 adet</Text>}
          />
          <List.Item
            title="Ürün B Çıkış"
            description="24.03.2024"
            left={props => <List.Icon {...props} icon="arrow-up" color="red" />}
            right={props => <Text>-20 adet</Text>}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Stok Raporları</Title>
          <Button mode="outlined" style={styles.reportButton}>
            Stok Durum Raporu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Hareket Raporu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Kritik Stok Raporu
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
  stockLevel: {
    fontWeight: 'bold',
    color: 'red',
  },
  reportButton: {
    marginBottom: 10,
  },
});

export default InventoryScreen; 