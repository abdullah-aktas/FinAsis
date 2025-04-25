import React from 'react';
import { View, ScrollView, StyleSheet, Image } from 'react-native';
import { Card, Title, Text, Button, Avatar } from 'react-native-paper';

const ProfileScreen = () => {
  return (
    <ScrollView style={styles.container}>
      <Card style={styles.profileCard}>
        <Card.Content style={styles.profileContent}>
          <Avatar.Image
            size={100}
            source={{ uri: 'https://randomuser.me/api/portraits/men/1.jpg' }}
            style={styles.avatar}
          />
          <Title style={styles.name}>Ahmet Yılmaz</Title>
          <Text style={styles.email}>ahmet.yilmaz@example.com</Text>
          <Button mode="contained" style={styles.editButton}>
            Profili Düzenle
          </Button>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Hesap Bilgileri</Title>
          <View style={styles.infoItem}>
            <Text>Üyelik Durumu</Text>
            <Text style={styles.infoValue}>Premium</Text>
          </View>
          <View style={styles.infoItem}>
            <Text>Üyelik Başlangıcı</Text>
            <Text style={styles.infoValue}>01.01.2024</Text>
          </View>
          <View style={styles.infoItem}>
            <Text>Son Giriş</Text>
            <Text style={styles.infoValue}>25.04.2024</Text>
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Güvenlik</Title>
          <Button mode="outlined" style={styles.securityButton}>
            Şifre Değiştir
          </Button>
          <Button mode="outlined" style={styles.securityButton}>
            İki Faktörlü Doğrulama
          </Button>
          <Button mode="outlined" style={styles.securityButton}>
            Oturum Geçmişi
          </Button>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Tercihler</Title>
          <Button mode="outlined" style={styles.preferenceButton}>
            Bildirim Ayarları
          </Button>
          <Button mode="outlined" style={styles.preferenceButton}>
            Tema Ayarları
          </Button>
          <Button mode="outlined" style={styles.preferenceButton}>
            Dil Ayarları
          </Button>
        </Card.Content>
      </Card>

      <Button mode="contained" style={styles.logoutButton}>
        Çıkış Yap
      </Button>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
    backgroundColor: '#f5f5f5',
  },
  profileCard: {
    marginBottom: 10,
    elevation: 4,
  },
  profileContent: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  avatar: {
    marginBottom: 10,
  },
  name: {
    fontSize: 24,
    marginBottom: 5,
  },
  email: {
    color: '#666',
    marginBottom: 15,
  },
  editButton: {
    marginTop: 10,
  },
  card: {
    marginBottom: 10,
    elevation: 4,
  },
  infoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  infoValue: {
    fontWeight: 'bold',
  },
  securityButton: {
    marginBottom: 10,
  },
  preferenceButton: {
    marginBottom: 10,
  },
  logoutButton: {
    marginTop: 20,
    marginBottom: 30,
    backgroundColor: '#ff4444',
  },
});

export default ProfileScreen; 