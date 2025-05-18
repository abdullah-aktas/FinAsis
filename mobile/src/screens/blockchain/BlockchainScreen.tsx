import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Button, Text, List } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';

const BlockchainScreen = () => {
  const navigation = useNavigation();

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Blockchain İşlemleri</Title>
          <View style={styles.buttonContainer}>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('DocumentVerification')}
            >
              Belge Doğrulama
            </Button>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('SmartContracts')}
            >
              Akıllı Sözleşmeler
            </Button>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Son İşlemler</Title>
          <List.Item
            title="Belge Doğrulama"
            description="Fatura #2024-001 - 25.03.2024"
            left={props => <List.Icon {...props} icon="shield-check" color="green" />}
            right={props => <Text style={styles.transactionStatus}>Onaylandı</Text>}
          />
          <List.Item
            title="Akıllı Sözleşme"
            description="Sözleşme #2024-002 - 24.03.2024"
            left={props => <List.Icon {...props} icon="file-document-check" color="blue" />}
            right={props => <Text style={styles.transactionStatus}>İşlemde</Text>}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Blockchain İstatistikleri</Title>
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>125</Text>
              <Text style={styles.statLabel}>Toplam İşlem</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>98%</Text>
              <Text style={styles.statLabel}>Başarı Oranı</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>45</Text>
              <Text style={styles.statLabel}>Aktif Sözleşme</Text>
            </View>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Akıllı Sözleşmeler</Title>
          <List.Item
            title="Ödeme Sözleşmesi"
            description="Otomatik ödeme sistemi"
            left={props => <List.Icon {...props} icon="cash" />}
            right={props => <Text style={styles.contractStatus}>Aktif</Text>}
          />
          <List.Item
            title="Tedarik Sözleşmesi"
            description="Otomatik tedarik sistemi"
            left={props => <List.Icon {...props} icon="truck" />}
            right={props => <Text style={styles.contractStatus}>Aktif</Text>}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Blockchain Raporları</Title>
          <Button mode="outlined" style={styles.reportButton}>
            İşlem Raporu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Sözleşme Raporu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Performans Raporu
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
  transactionStatus: {
    color: 'green',
    fontWeight: 'bold',
  },
  contractStatus: {
    color: 'blue',
    fontWeight: 'bold',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 10,
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#6200ee',
  },
  statLabel: {
    fontSize: 12,
    color: 'gray',
  },
  reportButton: {
    marginBottom: 10,
  },
});

export default BlockchainScreen; 