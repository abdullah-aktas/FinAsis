import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Image } from 'react-native';

const ProfileScreen = ({ navigation }) => {
  const userStats = {
    totalCourses: 3,
    completedCourses: 1,
    totalGames: 3,
    totalScore: 2050,
    badges: 2,
  };

  const badges = [
    {
      id: '1',
      name: 'Başlangıç',
      description: 'İlk kursu tamamladınız',
      icon: 'https://via.placeholder.com/50',
    },
    {
      id: '2',
      name: 'Oyun Ustası',
      description: '1000 puan topladınız',
      icon: 'https://via.placeholder.com/50',
    },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Image
          source={{ uri: 'https://via.placeholder.com/100' }}
          style={styles.profileImage}
        />
        <Text style={styles.userName}>Kullanıcı Adı</Text>
        <Text style={styles.userEmail}>kullanici@email.com</Text>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{userStats.totalCourses}</Text>
          <Text style={styles.statLabel}>Toplam Kurs</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{userStats.completedCourses}</Text>
          <Text style={styles.statLabel}>Tamamlanan</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{userStats.totalGames}</Text>
          <Text style={styles.statLabel}>Oyunlar</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>{userStats.totalScore}</Text>
          <Text style={styles.statLabel}>Toplam Puan</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Rozetlerim</Text>
        <View style={styles.badgesContainer}>
          {badges.map(badge => (
            <View key={badge.id} style={styles.badgeItem}>
              <Image
                source={{ uri: badge.icon }}
                style={styles.badgeIcon}
              />
              <Text style={styles.badgeName}>{badge.name}</Text>
              <Text style={styles.badgeDescription}>{badge.description}</Text>
            </View>
          ))}
        </View>
      </View>

      <TouchableOpacity style={styles.settingsButton}>
        <Text style={styles.settingsButtonText}>Ayarlar</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#2196F3',
  },
  profileImage: {
    width: 100,
    height: 100,
    borderRadius: 50,
    marginBottom: 10,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  userEmail: {
    fontSize: 16,
    color: '#fff',
    marginTop: 5,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 5,
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  badgesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  badgeItem: {
    width: '48%',
    backgroundColor: '#f5f5f5',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    alignItems: 'center',
  },
  badgeIcon: {
    width: 50,
    height: 50,
    marginBottom: 10,
  },
  badgeName: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  badgeDescription: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  settingsButton: {
    margin: 20,
    padding: 15,
    backgroundColor: '#2196F3',
    borderRadius: 10,
    alignItems: 'center',
  },
  settingsButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default ProfileScreen; 