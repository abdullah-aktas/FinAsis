import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { Notification } from '../types';
import Icon from 'react-native-vector-icons/MaterialIcons';

const NotificationDetailScreen = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const notification = route.params?.notification as Notification;

  const getNotificationIcon = () => {
    switch (notification.type) {
      case 'info':
        return 'info';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      case 'success':
        return 'check-circle';
      default:
        return 'notifications';
    }
  };

  const getNotificationColor = () => {
    switch (notification.type) {
      case 'info':
        return '#007AFF';
      case 'warning':
        return '#FF9500';
      case 'error':
        return '#FF3B30';
      case 'success':
        return '#34C759';
      default:
        return '#007AFF';
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Icon
          name={getNotificationIcon()}
          size={40}
          color={getNotificationColor()}
          style={styles.icon}
        />
        <Text style={styles.title}>{notification.title}</Text>
        <Text style={styles.time}>
          {new Date(notification.created_at).toLocaleString('tr-TR')}
        </Text>
      </View>

      <View style={styles.content}>
        <Text style={styles.message}>{notification.message}</Text>
      </View>

      <TouchableOpacity
        style={styles.backButton}
        onPress={() => navigation.goBack()}
      >
        <Icon name="arrow-back" size={24} color="#fff" />
        <Text style={styles.backButtonText}>Geri Dön</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  icon: {
    marginBottom: 15,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 10,
  },
  time: {
    fontSize: 14,
    color: '#999',
  },
  content: {
    backgroundColor: '#fff',
    padding: 20,
    marginTop: 10,
  },
  message: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
  },
  backButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#007AFF',
    padding: 15,
    margin: 20,
    borderRadius: 10,
  },
  backButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 10,
  },
});

export default NotificationDetailScreen; 