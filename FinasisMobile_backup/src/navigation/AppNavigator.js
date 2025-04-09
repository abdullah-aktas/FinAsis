import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

// Ekranlar
import HomeScreen from '../screens/HomeScreen';
import EducationScreen from '../screens/EducationScreen';
import GameScreen from '../screens/GameScreen';
import ProfileScreen from '../screens/ProfileScreen';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

const MainTabs = () => {
  return (
    <Tab.Navigator>
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          title: 'Ana Sayfa'
        }}
      />
      <Tab.Screen 
        name="Education" 
        component={EducationScreen}
        options={{
          title: 'Eğitim'
        }}
      />
      <Tab.Screen 
        name="Game" 
        component={GameScreen}
        options={{
          title: 'Oyunlar'
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          title: 'Profil'
        }}
      />
    </Tab.Navigator>
  );
};

const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen 
          name="MainTabs" 
          component={MainTabs}
          options={{ headerShown: false }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator; 