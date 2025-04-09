import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Image } from 'react-native';

const GameScreen = ({ navigation }) => {
  const games = [
    {
      id: '1',
      title: 'Finansal Kelime Oyunu',
      description: 'Finansal terimleri öğrenin ve puan kazanın',
      image: 'https://via.placeholder.com/150',
      highScore: 850,
    },
    {
      id: '2',
      title: 'Bütçe Simülasyonu',
      description: 'Gerçek hayat senaryolarıyla bütçe yönetimini öğrenin',
      image: 'https://via.placeholder.com/150',
      highScore: 1200,
    },
    {
      id: '3',
      title: 'Yatırım Yarışması',
      description: 'Yatırım stratejilerinizi test edin',
      image: 'https://via.placeholder.com/150',
      highScore: 0,
    },
  ];

  const renderGameItem = ({ item }) => (
    <TouchableOpacity 
      style={styles.gameCard}
      onPress={() => navigation.navigate('GameDetail', { gameId: item.id })}
    >
      <Image
        source={{ uri: item.image }}
        style={styles.gameImage}
      />
      <View style={styles.gameInfo}>
        <Text style={styles.gameTitle}>{item.title}</Text>
        <Text style={styles.gameDescription}>{item.description}</Text>
        <Text style={styles.highScore}>En Yüksek Skor: {item.highScore}</Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Oyunlar</Text>
      <FlatList
        data={games}
        renderItem={renderGameItem}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.listContainer}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    padding: 20,
    backgroundColor: '#2196F3',
    color: '#fff',
  },
  listContainer: {
    padding: 15,
  },
  gameCard: {
    flexDirection: 'row',
    backgroundColor: '#f5f5f5',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
  },
  gameImage: {
    width: 100,
    height: 100,
    borderRadius: 10,
    marginRight: 15,
  },
  gameInfo: {
    flex: 1,
  },
  gameTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  gameDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  highScore: {
    fontSize: 12,
    color: '#2196F3',
    fontWeight: 'bold',
  },
});

export default GameScreen; 