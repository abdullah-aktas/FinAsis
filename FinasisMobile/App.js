import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { StyleSheet, Text, View, TouchableOpacity, Image, ScrollView, SafeAreaView } from 'react-native';
import { FontAwesome, MaterialIcons, Ionicons } from '@expo/vector-icons';

// Ana ekran bileşeni
function HomeScreen({ navigation }) {
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Image 
            source={require('./assets/logo.png')} 
            style={styles.logo}
            resizeMode="contain"
          />
          <Text style={styles.welcomeText}>Hoş Geldiniz</Text>
        </View>

        <View style={styles.heroSection}>
          <Text style={styles.heroTitle}>FinAsis</Text>
          <Text style={styles.heroSubtitle}>Finansal eğitim ve deneyim platformu</Text>
          <TouchableOpacity 
            style={styles.heroCta}
            onPress={() => navigation.navigate('Login')}
          >
            <Text style={styles.heroCtaText}>Hemen Başla</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.sectionTitle}>Özellikler</Text>
        
        <View style={styles.featuresContainer}>
          <TouchableOpacity 
            style={styles.featureCard}
            onPress={() => navigation.navigate('Education')}
          >
            <FontAwesome name="graduation-cap" size={48} color="#2193b0" style={styles.featureIcon} />
            <Text style={styles.featureTitle}>Eğitim</Text>
            <Text style={styles.featureText}>Finansal okuryazarlık eğitimleri ile bilgi ve becerilerinizi geliştirin.</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.featureCard}
            onPress={() => navigation.navigate('VirtualCompany')}
          >
            <FontAwesome name="building" size={48} color="#2193b0" style={styles.featureIcon} />
            <Text style={styles.featureTitle}>Sanal Şirket</Text>
            <Text style={styles.featureText}>Kendi sanal şirketinizi kurun ve gerçek dünya deneyimi kazanın.</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.featureCard}
            onPress={() => navigation.navigate('AIAssistant')}
          >
            <FontAwesome name="robot" size={48} color="#2193b0" style={styles.featureIcon} />
            <Text style={styles.featureTitle}>AI Asistan</Text>
            <Text style={styles.featureText}>Yapay zeka destekli asistanımız ile finansal sorularınıza anında yanıt alın.</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.featureCard}
            onPress={() => navigation.navigate('Blockchain')}
          >
            <FontAwesome name="link" size={48} color="#2193b0" style={styles.featureIcon} />
            <Text style={styles.featureTitle}>Blockchain</Text>
            <Text style={styles.featureText}>Blockchain teknolojisini keşfedin ve kripto para işlemleri yapın.</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.featureCard}
            onPress={() => navigation.navigate('Games')}
          >
            <FontAwesome name="gamepad" size={48} color="#2193b0" style={styles.featureIcon} />
            <Text style={styles.featureTitle}>Oyunlar</Text>
            <Text style={styles.featureText}>Eğitici finansal oyunlar ile eğlenerek öğrenin.</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// Eğitim ekranı
function EducationScreen() {
  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenTitle}>Eğitimler</Text>
      <Text>Eğitim içeriği burada görüntülenecek.</Text>
    </View>
  );
}

// Sanal Şirket ekranı
function VirtualCompanyScreen() {
  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenTitle}>Sanal Şirket</Text>
      <Text>Sanal şirket içeriği burada görüntülenecek.</Text>
    </View>
  );
}

// AI Asistan ekranı
function AIAssistantScreen() {
  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenTitle}>AI Asistan</Text>
      <Text>AI Asistan içeriği burada görüntülenecek.</Text>
    </View>
  );
}

// Blockchain ekranı
function BlockchainScreen() {
  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenTitle}>Blockchain</Text>
      <Text>Blockchain içeriği burada görüntülenecek.</Text>
    </View>
  );
}

// Oyunlar ekranı
function GamesScreen() {
  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenTitle}>Oyunlar</Text>
      <Text>Oyunlar içeriği burada görüntülenecek.</Text>
    </View>
  );
}

// Profil ekranı
function ProfileScreen() {
  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenTitle}>Profil</Text>
      <Text>Profil içeriği burada görüntülenecek.</Text>
    </View>
  );
}

// Giriş ekranı
function LoginScreen({ navigation }) {
  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenTitle}>Giriş Yap</Text>
      <Text>Giriş formu burada görüntülenecek.</Text>
      <TouchableOpacity 
        style={styles.button}
        onPress={() => navigation.navigate('Register')}
      >
        <Text style={styles.buttonText}>Hesabınız yok mu? Kayıt Ol</Text>
      </TouchableOpacity>
    </View>
  );
}

// Kayıt ekranı
function RegisterScreen() {
  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenTitle}>Kayıt Ol</Text>
      <Text>Kayıt formu burada görüntülenecek.</Text>
    </View>
  );
}

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Ana tab navigasyonu
function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Ana Sayfa') {
            iconName = 'home';
            return <FontAwesome name={iconName} size={size} color={color} />;
          } else if (route.name === 'Eğitimler') {
            iconName = 'graduation-cap';
            return <FontAwesome name={iconName} size={size} color={color} />;
          } else if (route.name === 'Sanal Şirket') {
            iconName = 'building';
            return <FontAwesome name={iconName} size={size} color={color} />;
          } else if (route.name === 'AI Asistan') {
            iconName = 'robot';
            return <MaterialIcons name="smart-toy" size={size} color={color} />;
          } else if (route.name === 'Profil') {
            iconName = 'user';
            return <FontAwesome name={iconName} size={size} color={color} />;
          }
        },
        tabBarActiveTintColor: '#2193b0',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="Ana Sayfa" component={HomeScreen} />
      <Tab.Screen name="Eğitimler" component={EducationScreen} />
      <Tab.Screen name="Sanal Şirket" component={VirtualCompanyScreen} />
      <Tab.Screen name="AI Asistan" component={AIAssistantScreen} />
      <Tab.Screen name="Profil" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

// Ana uygulama
export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Main" screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Main" component={MainTabNavigator} />
        <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: true }} />
        <Stack.Screen name="Register" component={RegisterScreen} options={{ headerShown: true }} />
        <Stack.Screen name="Education" component={EducationScreen} options={{ headerShown: true }} />
        <Stack.Screen name="VirtualCompany" component={VirtualCompanyScreen} options={{ headerShown: true }} />
        <Stack.Screen name="AIAssistant" component={AIAssistantScreen} options={{ headerShown: true }} />
        <Stack.Screen name="Blockchain" component={BlockchainScreen} options={{ headerShown: true }} />
        <Stack.Screen name="Games" component={GamesScreen} options={{ headerShown: true }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// Stiller
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f8f8',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#fff',
    elevation: 2,
  },
  logo: {
    width: 120,
    height: 40,
  },
  welcomeText: {
    fontSize: 16,
    color: '#333',
  },
  heroSection: {
    backgroundColor: '#2193b0',
    padding: 24,
    alignItems: 'center',
    marginHorizontal: 16,
    marginTop: 16,
    borderRadius: 16,
  },
  heroTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  heroSubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: 24,
    textAlign: 'center',
  },
  heroCta: {
    backgroundColor: '#fff',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 24,
  },
  heroCtaText: {
    color: '#2193b0',
    fontWeight: 'bold',
    fontSize: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    margin: 16,
  },
  featuresContainer: {
    paddingHorizontal: 8,
  },
  featureCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    marginHorizontal: 8,
    marginBottom: 16,
    elevation: 2,
  },
  featureIcon: {
    marginBottom: 12,
  },
  featureTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2193b0',
    marginBottom: 8,
  },
  featureText: {
    color: '#666',
    lineHeight: 20,
  },
  screenContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  screenTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  button: {
    marginTop: 16,
    backgroundColor: '#2193b0',
    padding: 12,
    borderRadius: 8,
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
    textAlign: 'center',
  }
});
