import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Provider as PaperProvider } from 'react-native-paper';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// Ana Ekranlar
import HomeScreen from './src/screens/HomeScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';
import SettingsScreen from './src/screens/SettingsScreen';

// Muhasebe Modülü
import AccountingScreen from './src/screens/accounting/AccountingScreen';
import ChartOfAccountsScreen from './src/screens/accounting/ChartOfAccountsScreen';
import InvoiceScreen from './src/screens/accounting/InvoiceScreen';

// Finans Modülü
import FinanceScreen from './src/screens/finance/FinanceScreen';
import BankTransactionsScreen from './src/screens/finance/BankTransactionsScreen';
import CashFlowScreen from './src/screens/finance/CashFlowScreen';

// CRM Modülü
import CRMScreen from './src/screens/crm/CRMScreen';
import CustomersScreen from './src/screens/crm/CustomersScreen';
import OpportunitiesScreen from './src/screens/crm/OpportunitiesScreen';

// Stok Modülü
import InventoryScreen from './src/screens/inventory/InventoryScreen';
import ProductsScreen from './src/screens/inventory/ProductsScreen';
import StockCountScreen from './src/screens/inventory/StockCountScreen';

// İK Modülü
import HRScreen from './src/screens/hr/HRScreen';
import EmployeesScreen from './src/screens/hr/EmployeesScreen';
import PayrollScreen from './src/screens/hr/PayrollScreen';

// Sanal Şirket Modülü
import VirtualCompanyScreen from './src/screens/virtual/VirtualCompanyScreen';
import CompanyListScreen from './src/screens/virtual/CompanyListScreen';
import SimulationScreen from './src/screens/virtual/SimulationScreen';

// Belgeler Modülü
import DocumentsScreen from './src/screens/documents/DocumentsScreen';
import EInvoiceScreen from './src/screens/documents/EInvoiceScreen';

// Blockchain Modülü
import BlockchainScreen from './src/screens/blockchain/BlockchainScreen';
import DocumentVerificationScreen from './src/screens/blockchain/DocumentVerificationScreen';

// AI Asistan Modülü
import AIScreen from './src/screens/ai/AIScreen';
import PredictionsScreen from './src/screens/ai/PredictionsScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

const MainTabs = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Ana Sayfa') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Muhasebe') {
            iconName = focused ? 'calculator' : 'calculator-outline';
          } else if (route.name === 'Finans') {
            iconName = focused ? 'bank' : 'bank-outline';
          } else if (route.name === 'CRM') {
            iconName = focused ? 'account-group' : 'account-group-outline';
          } else if (route.name === 'Stok') {
            iconName = focused ? 'package-variant' : 'package-variant-closed';
          } else if (route.name === 'İK') {
            iconName = focused ? 'account-tie' : 'account-tie-outline';
          } else if (route.name === 'Sanal Şirket') {
            iconName = focused ? 'office-building' : 'office-building-outline';
          } else if (route.name === 'Belgeler') {
            iconName = focused ? 'file-document' : 'file-document-outline';
          } else if (route.name === 'Blockchain') {
            iconName = focused ? 'blockchain' : 'blockchain-outline';
          } else if (route.name === 'AI') {
            iconName = focused ? 'robot' : 'robot-outline';
          } else if (route.name === 'Analitik') {
            iconName = focused ? 'chart-line' : 'chart-line-variant';
          } else if (route.name === 'Profil') {
            iconName = focused ? 'account' : 'account-outline';
          } else if (route.name === 'Ayarlar') {
            iconName = focused ? 'cog' : 'cog-outline';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6200ee',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="Ana Sayfa" component={HomeScreen} />
      <Tab.Screen name="Muhasebe" component={AccountingScreen} />
      <Tab.Screen name="Finans" component={FinanceScreen} />
      <Tab.Screen name="CRM" component={CRMScreen} />
      <Tab.Screen name="Stok" component={InventoryScreen} />
      <Tab.Screen name="İK" component={HRScreen} />
      <Tab.Screen name="Sanal Şirket" component={VirtualCompanyScreen} />
      <Tab.Screen name="Belgeler" component={DocumentsScreen} />
      <Tab.Screen name="Blockchain" component={BlockchainScreen} />
      <Tab.Screen name="AI" component={AIScreen} />
      <Tab.Screen name="Analitik" component={AnalyticsScreen} />
      <Tab.Screen name="Profil" component={ProfileScreen} />
      <Tab.Screen name="Ayarlar" component={SettingsScreen} />
    </Tab.Navigator>
  );
};

export default function App() {
  return (
    <SafeAreaProvider>
      <PaperProvider>
        <NavigationContainer>
          <Stack.Navigator>
            <Stack.Screen 
              name="MainTabs" 
              component={MainTabs} 
              options={{ headerShown: false }}
            />
            {/* Muhasebe Modülü */}
            <Stack.Screen name="ChartOfAccounts" component={ChartOfAccountsScreen} />
            <Stack.Screen name="Invoice" component={InvoiceScreen} />
            
            {/* Finans Modülü */}
            <Stack.Screen name="BankTransactions" component={BankTransactionsScreen} />
            <Stack.Screen name="CashFlow" component={CashFlowScreen} />
            
            {/* CRM Modülü */}
            <Stack.Screen name="Customers" component={CustomersScreen} />
            <Stack.Screen name="Opportunities" component={OpportunitiesScreen} />
            
            {/* Stok Modülü */}
            <Stack.Screen name="Products" component={ProductsScreen} />
            <Stack.Screen name="StockCount" component={StockCountScreen} />
            
            {/* İK Modülü */}
            <Stack.Screen name="Employees" component={EmployeesScreen} />
            <Stack.Screen name="Payroll" component={PayrollScreen} />
            
            {/* Sanal Şirket Modülü */}
            <Stack.Screen name="CompanyList" component={CompanyListScreen} />
            <Stack.Screen name="Simulation" component={SimulationScreen} />
            
            {/* Belgeler Modülü */}
            <Stack.Screen name="EInvoice" component={EInvoiceScreen} />
            
            {/* Blockchain Modülü */}
            <Stack.Screen name="DocumentVerification" component={DocumentVerificationScreen} />
            
            {/* AI Modülü */}
            <Stack.Screen name="Predictions" component={PredictionsScreen} />
          </Stack.Navigator>
        </NavigationContainer>
      </PaperProvider>
    </SafeAreaProvider>
  );
} 