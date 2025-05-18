import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { STORAGE_KEYS } from '../config';
import Icon from 'react-native-vector-icons/Feather';
import { UserProvider, useUser } from '../contexts/UserContext';

// Screens
import LoginScreen from '../screens/auth/LoginScreen';
import TwoFactorScreen from '../screens/auth/TwoFactorScreen';
import HomeScreen from '../screens/HomeScreen';
import ProfileScreen from '../screens/ProfileScreen';
import NotificationsScreen from '../screens/NotificationsScreen';
import CourseListScreen from '../screens/education/CourseListScreen';
import CourseDetailScreen from '../screens/education/CourseDetailScreen';
import LessonDetailScreen from '../screens/education/LessonDetailScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

const AuthStack = () => {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="TwoFactor" component={TwoFactorScreen} />
    </Stack.Navigator>
  );
};

const EducationStack = createStackNavigator();
const EducationStackScreen = () => (
  <EducationStack.Navigator>
    <EducationStack.Screen name="CourseList" component={CourseListScreen} options={{ title: 'Kurslar' }} />
    <EducationStack.Screen name="CourseDetail" component={CourseDetailScreen} options={{ title: 'Kurs Detayı' }} />
    <EducationStack.Screen name="LessonDetail" component={LessonDetailScreen} options={{ title: 'Ders Detayı' }} />
  </EducationStack.Navigator>
);

const MainTabs = () => {
  const { user } = useUser();
  if (!user) return null;
  const tabs = [];
  // Rol bazlı sekmeler
  if (['student', 'teacher', 'admin'].includes(user.role)) {
    tabs.push(
      <Tab.Screen
        key="Education"
        name="Education"
        component={EducationStackScreen}
        options={{
          tabBarLabel: 'Eğitim',
          tabBarIcon: ({ color, size }) => (
            <Icon name="book-open" size={size} color={color} />
          ),
        }}
      />
    );
  }
  if (['accountant', 'admin'].includes(user.role)) {
    tabs.push(
      <Tab.Screen
        key="Accounting"
        name="Accounting"
        component={AccountingStackScreen}
        options={{
          tabBarLabel: 'Muhasebe',
          tabBarIcon: ({ color, size }) => (
            <Icon name="file-text" size={size} color={color} />
          ),
        }}
      />
    );
  }
  if (['hr', 'admin'].includes(user.role)) {
    tabs.push(
      <Tab.Screen
        key="HR"
        name="HR"
        component={HRStackScreen}
        options={{
          tabBarLabel: 'İK',
          tabBarIcon: ({ color, size }) => (
            <Icon name="users" size={size} color={color} />
          ),
        }}
      />
    );
  }
  if (['crm', 'admin'].includes(user.role)) {
    tabs.push(
      <Tab.Screen
        key="CRM"
        name="CRM"
        component={CRMStackScreen}
        options={{
          tabBarLabel: 'CRM',
          tabBarIcon: ({ color, size }) => (
            <Icon name="briefcase" size={size} color={color} />
          ),
        }}
      />
    );
  }
  // Ortak sekmeler
  tabs.push(
    <Tab.Screen
      key="Notifications"
      name="Notifications"
      component={NotificationsScreen}
      options={{
        tabBarLabel: 'Bildirimler',
        tabBarIcon: ({ color, size }) => (
          <Icon name="bell" size={size} color={color} />
        ),
      }}
    />,
    <Tab.Screen
      key="Profile"
      name="Profile"
      component={ProfileScreen}
      options={{
        tabBarLabel: 'Profil',
        tabBarIcon: ({ color, size }) => (
          <Icon name="user" size={size} color={color} />
        ),
      }}
    />
  );
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#999',
        headerShown: false,
      }}
    >
      {tabs}
    </Tab.Navigator>
  );
};

const AppNavigator = () => {
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = await AsyncStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
      setIsAuthenticated(!!token);
    } catch (error) {
      console.error('Auth check error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return null; // veya bir yükleme ekranı
  }

  return (
    <UserProvider>
      <NavigationContainer>
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          {isAuthenticated ? (
            <Stack.Screen name="Main" component={MainTabs} />
          ) : (
            <Stack.Screen name="Auth" component={AuthStack} />
          )}
        </Stack.Navigator>
      </NavigationContainer>
    </UserProvider>
  );
};

export default AppNavigator; 