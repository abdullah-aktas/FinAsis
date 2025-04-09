import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';

const EducationScreen = ({ navigation }) => {
  const courses = [
    {
      id: '1',
      title: 'Temel Finansal Kavramlar',
      description: 'Finansal okuryazarlığın temellerini öğrenin',
      progress: 75,
    },
    {
      id: '2',
      title: 'Bütçe Yönetimi',
      description: 'Kişisel bütçe oluşturma ve yönetme',
      progress: 30,
    },
    {
      id: '3',
      title: 'Yatırım Temelleri',
      description: 'Yatırım araçları ve stratejileri',
      progress: 0,
    },
  ];

  const renderCourseItem = ({ item }) => (
    <TouchableOpacity 
      style={styles.courseCard}
      onPress={() => navigation.navigate('CourseDetail', { courseId: item.id })}
    >
      <Text style={styles.courseTitle}>{item.title}</Text>
      <Text style={styles.courseDescription}>{item.description}</Text>
      <View style={styles.progressBar}>
        <View style={[styles.progressFill, { width: `${item.progress}%` }]} />
      </View>
      <Text style={styles.progressText}>{item.progress}% Tamamlandı</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Eğitimler</Text>
      <FlatList
        data={courses}
        renderItem={renderCourseItem}
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
  courseCard: {
    backgroundColor: '#f5f5f5',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
  },
  courseTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  courseDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  progressBar: {
    height: 5,
    backgroundColor: '#ddd',
    borderRadius: 3,
    marginBottom: 5,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#2196F3',
    borderRadius: 3,
  },
  progressText: {
    fontSize: 12,
    color: '#666',
  },
});

export default EducationScreen; 