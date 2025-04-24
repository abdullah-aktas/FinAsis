import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { authService } from '../../services/api';
import { STORAGE_KEYS } from '../../config';
import AsyncStorage from '@react-native-async-storage/async-storage';

const TwoFactorScreen = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);

  const handleVerify = async () => {
    if (!code) {
      Alert.alert('Hata', 'Lütfen doğrulama kodunu girin.');
      return;
    }

    setLoading(true);
    try {
      const deviceId = route.params?.deviceId;
      const response = await authService.verifyTwoFactor(deviceId, code);

      if (response.status === 'success') {
        await AsyncStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, response.access_token!);
        await AsyncStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.refresh_token!);
        await AsyncStorage.setItem(STORAGE_KEYS.USER_INFO, JSON.stringify(response.user));
        navigation.reset({
          index: 0,
          routes: [{ name: 'Home' }],
        });
      } else {
        Alert.alert('Hata', response.message || 'Doğrulama başarısız oldu.');
      }
    } catch (error) {
      Alert.alert('Hata', 'Doğrulama yapılırken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>İki Faktörlü Doğrulama</Text>
      <Text style={styles.subtitle}>
        Lütfen telefonunuza gönderilen doğrulama kodunu girin.
      </Text>
      <View style={styles.form}>
        <TextInput
          style={styles.input}
          placeholder="Doğrulama Kodu"
          value={code}
          onChangeText={setCode}
          keyboardType="number-pad"
          maxLength={6}
        />
        <TouchableOpacity
          style={styles.button}
          onPress={handleVerify}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Doğrula</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 30,
    color: '#666',
  },
  form: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    paddingHorizontal: 15,
    marginBottom: 15,
    fontSize: 16,
    textAlign: 'center',
    letterSpacing: 5,
  },
  button: {
    backgroundColor: '#007AFF',
    height: 50,
    borderRadius: 5,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default TwoFactorScreen; 