import React from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Button, Text, List } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';

const DocumentsScreen = () => {
  const navigation = useNavigation();

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Belge İşlemleri</Title>
          <View style={styles.buttonContainer}>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('EInvoice')}
            >
              E-Fatura
            </Button>
            <Button 
              mode="contained" 
              style={styles.button}
              onPress={() => navigation.navigate('DocumentArchive')}
            >
              Belge Arşivi
            </Button>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Son Belgeler</Title>
          <List.Item
            title="Fatura #2024-001"
            description="ABC Yazılım A.Ş. - 25.03.2024"
            left={props => <List.Icon {...props} icon="file-document" />}
            right={props => <Text style={styles.documentStatus}>Onaylandı</Text>}
          />
          <List.Item
            title="Sözleşme #2024-002"
            description="XYZ Danışmanlık - 24.03.2024"
            left={props => <List.Icon {...props} icon="file-document" />}
            right={props => <Text style={styles.documentStatus}>Beklemede</Text>}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>E-Fatura İşlemleri</Title>
          <Button mode="outlined" style={styles.actionButton}>
            Yeni E-Fatura Oluştur
          </Button>
          <Button mode="outlined" style={styles.actionButton}>
            E-Fatura Gönder
          </Button>
          <Button mode="outlined" style={styles.actionButton}>
            E-Fatura Arşivi
          </Button>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Belge Kategorileri</Title>
          <List.Item
            title="Faturalar"
            description="Tüm fatura belgeleri"
            left={props => <List.Icon {...props} icon="receipt" />}
            right={props => <Text>25 belge</Text>}
          />
          <List.Item
            title="Sözleşmeler"
            description="Tüm sözleşme belgeleri"
            left={props => <List.Icon {...props} icon="file-document-edit" />}
            right={props => <Text>15 belge</Text>}
          />
          <List.Item
            title="Raporlar"
            description="Tüm rapor belgeleri"
            left={props => <List.Icon {...props} icon="file-chart" />}
            right={props => <Text>10 belge</Text>}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Belge Raporları</Title>
          <Button mode="outlined" style={styles.reportButton}>
            Belge Durum Raporu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            E-Fatura Raporu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Arşiv Raporu
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
  documentStatus: {
    color: 'green',
    fontWeight: 'bold',
  },
  actionButton: {
    marginBottom: 10,
  },
  reportButton: {
    marginBottom: 10,
  },
});

export default DocumentsScreen; 