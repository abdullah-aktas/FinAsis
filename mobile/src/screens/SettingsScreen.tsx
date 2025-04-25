import React, { useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Card, Title, Switch, Button, Text, List } from 'react-native-paper';

const SettingsScreen = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);
  const [biometricAuth, setBiometricAuth] = useState(false);
  const [autoSync, setAutoSync] = useState(true);

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Görünüm</Title>
          <List.Item
            title="Karanlık Mod"
            description="Uygulamayı karanlık temada kullan"
            right={() => (
              <Switch
                value={darkMode}
                onValueChange={setDarkMode}
              />
            )}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Bildirimler</Title>
          <List.Item
            title="Bildirimleri Etkinleştir"
            description="Önemli güncellemeler ve hatırlatıcılar için bildirim al"
            right={() => (
              <Switch
                value={notifications}
                onValueChange={setNotifications}
              />
            )}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Güvenlik</Title>
          <List.Item
            title="Biyometrik Kimlik Doğrulama"
            description="Parmak izi veya yüz tanıma ile giriş yap"
            right={() => (
              <Switch
                value={biometricAuth}
                onValueChange={setBiometricAuth}
              />
            )}
          />
          <List.Item
            title="Otomatik Senkronizasyon"
            description="Verileri otomatik olarak senkronize et"
            right={() => (
              <Switch
                value={autoSync}
                onValueChange={setAutoSync}
              />
            )}
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Veri Yönetimi</Title>
          <Button mode="outlined" style={styles.button}>
            Verileri Yedekle
          </Button>
          <Button mode="outlined" style={styles.button}>
            Önbelleği Temizle
          </Button>
          <Button mode="outlined" style={styles.button}>
            Uygulama Verilerini Sıfırla
          </Button>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Hakkında</Title>
          <Text style={styles.version}>Versiyon 1.0.0</Text>
          <Button mode="outlined" style={styles.button}>
            Gizlilik Politikası
          </Button>
          <Button mode="outlined" style={styles.button}>
            Kullanım Koşulları
          </Button>
          <Button mode="outlined" style={styles.button}>
            Yardım ve Destek
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
  button: {
    marginBottom: 10,
  },
  version: {
    textAlign: 'center',
    marginBottom: 15,
    color: '#666',
  },
});

export default SettingsScreen; 