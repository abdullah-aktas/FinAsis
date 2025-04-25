import React, { useState } from 'react';
import { View, ScrollView, StyleSheet, TextInput } from 'react-native';
import { Card, Title, Button, Text, List, Avatar } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';

const AIScreen = () => {
  const navigation = useNavigation();
  const [message, setMessage] = useState('');

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>AI Asistan</Title>
          <View style={styles.chatContainer}>
            <View style={styles.messageContainer}>
              <Avatar.Text size={30} label="AI" style={styles.avatar} />
              <View style={styles.messageBubble}>
                <Text>Merhaba! Size nasıl yardımcı olabilirim?</Text>
              </View>
            </View>
            <View style={[styles.messageContainer, styles.userMessage]}>
              <View style={styles.messageBubble}>
                <Text>Finansal raporumu analiz edebilir misin?</Text>
              </View>
              <Avatar.Text size={30} label="K" style={styles.avatar} />
            </View>
          </View>
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.input}
              placeholder="Mesajınızı yazın..."
              value={message}
              onChangeText={setMessage}
            />
            <Button mode="contained" onPress={() => {}}>
              Gönder
            </Button>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>AI Özellikleri</Title>
          <List.Item
            title="Finansal Analiz"
            description="Gelir-gider analizi ve tahminler"
            left={props => <List.Icon {...props} icon="chart-line" />}
          />
          <List.Item
            title="Belge İşleme"
            description="Otomatik belge analizi ve sınıflandırma"
            left={props => <List.Icon {...props} icon="file-document" />}
          />
          <List.Item
            title="Müşteri Analizi"
            description="Müşteri davranışı ve trend analizi"
            left={props => <List.Icon {...props} icon="account-group" />}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Son Analizler</Title>
          <List.Item
            title="Finansal Tahmin"
            description="3 aylık gelir tahmini"
            left={props => <List.Icon {...props} icon="chart-bar" color="blue" />}
            right={props => <Text style={styles.analysisStatus}>Tamamlandı</Text>}
          />
          <List.Item
            title="Müşteri Segmentasyonu"
            description="Müşteri grupları analizi"
            left={props => <List.Icon {...props} icon="chart-pie" color="green" />}
            right={props => <Text style={styles.analysisStatus}>Tamamlandı</Text>}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>AI Raporları</Title>
          <Button mode="outlined" style={styles.reportButton}>
            Finansal Analiz Raporu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Müşteri Analiz Raporu
          </Button>
          <Button mode="outlined" style={styles.reportButton}>
            Trend Analiz Raporu
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
  chatContainer: {
    marginVertical: 10,
  },
  messageContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  userMessage: {
    justifyContent: 'flex-end',
  },
  avatar: {
    marginHorizontal: 8,
  },
  messageBubble: {
    backgroundColor: '#e0e0e0',
    padding: 10,
    borderRadius: 15,
    maxWidth: '80%',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
  },
  input: {
    flex: 1,
    marginRight: 10,
    backgroundColor: 'white',
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 8,
  },
  analysisStatus: {
    color: 'green',
    fontWeight: 'bold',
  },
  reportButton: {
    marginBottom: 10,
  },
});

export default AIScreen; 