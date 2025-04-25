import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Button, Text, List, Avatar } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { PieChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';

const HRScreen = () => {
  const navigation = useNavigation();
  const screenWidth = Dimensions.get('window').width;

  const data = [
    {
      name: "Yazılım",
      population: 15,
      color: "#FF6384",
      legendFontColor: "#7F7F7F",
      legendFontSize: 12
    },
    {
      name: "Pazarlama",
      population: 8,
      color: "#36A2EB",
      legendFontColor: "#7F7F7F",
      legendFontSize: 12
    },
    {
      name: "Satış",
      population: 12,
      color: "#FFCE56",
      legendFontColor: "#7F7F7F",
      legendFontSize: 12
    }
  ];

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>İK İşlemleri</Title>
          <View style={styles.buttonContainer}>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('Employees')}
            >
              Çalışanlar
            </Button>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('Payroll')}
            >
              Bordro
            </Button>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Çalışan Özeti</Title>
          <View style={styles.employeeItem}>
            <Avatar.Text size={40} label="AK" />
            <View style={styles.employeeInfo}>
              <Text style={styles.employeeName}>Ahmet Kaya</Text>
              <Text style={styles.employeePosition}>Yazılım Geliştirici</Text>
            </View>
            <Text style={styles.employeeStatus}>Aktif</Text>
          </View>
          <View style={styles.employeeItem}>
            <Avatar.Text size={40} label="MA" />
            <View style={styles.employeeInfo}>
              <Text style={styles.employeeName}>Mehmet Arslan</Text>
              <Text style={styles.employeePosition}>Pazarlama Uzmanı</Text>
            </View>
            <Text style={styles.employeeStatus}>İzinli</Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Departman Dağılımı</Title>
          <PieChart
            data={data}
            width={screenWidth - 40}
            height={220}
            chartConfig={{
              backgroundColor: '#ffffff',
              backgroundGradientFrom: '#ffffff',
              backgroundGradientTo: '#ffffff',
              decimalPlaces: 0,
              color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
            }}
            accessor="population"
            backgroundColor="transparent"
            paddingLeft="15"
            absolute
            style={styles.chart}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Son İşlemler</Title>
          <List.Item
            title="İzin Talebi"
            description="Ahmet Kaya - 25.03.2024"
            left={props => <List.Icon {...props} icon="calendar" color="blue" />}
            right={props => <Text>Onaylandı</Text>}
          />
          <List.Item
            title="Bordro Ödeme"
            description="Tüm Çalışanlar - 24.03.2024"
            left={props => <List.Icon {...props} icon="cash" color="green" />}
            right={props => <Text>Tamamlandı</Text>}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>İK Raporları</Title>
          <Button mode="outlined" style={styles.reportButton}>
            Çalışan Performans Raporu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            İzin Raporu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Bordro Raporu
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
  employeeItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  employeeInfo: {
    flex: 1,
    marginLeft: 10,
  },
  employeeName: {
    fontWeight: 'bold',
  },
  employeePosition: {
    color: 'gray',
    fontSize: 12,
  },
  employeeStatus: {
    color: 'green',
    fontWeight: 'bold',
  },
  reportButton: {
    marginBottom: 10,
  },
});

export default HRScreen; 