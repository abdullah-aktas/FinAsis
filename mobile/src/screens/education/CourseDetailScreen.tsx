import React, { useEffect, useState } from 'react';
import { View, Text, Image, FlatList, TouchableOpacity, ActivityIndicator, StyleSheet, ScrollView } from 'react-native';
import { educationService } from '../../services/api';
import { Course, Lesson } from '../../types';
import { useRoute, useNavigation } from '@react-navigation/native';

const CourseDetailScreen = () => {
  const route = useRoute<any>();
  const navigation = useNavigation();
  const { id } = route.params;
  const [course, setCourse] = useState<Course | null>(null);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    educationService.getCourse(id).then(setCourse);
    // Dersler için örnek: /api/education/courses/:id/lessons/ endpointi varsa kullanılabilir
    educationService.getCourseLessons?.(id).then(setLessons).finally(() => setLoading(false));
  }, [id]);

  if (loading || !course) {
    return <ActivityIndicator style={{ flex: 1 }} size="large" color="#007bff" />;
  }

  return (
    <ScrollView style={styles.container}>
      {course.image && <Image source={{ uri: course.image }} style={styles.image} />}
      <Text style={styles.title}>{course.title}</Text>
      <Text style={styles.desc}>{course.description}</Text>
      <Text style={styles.meta}>{course.level} | {course.duration} saat</Text>
      <Text style={styles.section}>Dersler</Text>
      <FlatList
        data={lessons}
        keyExtractor={item => item.id.toString()}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.lessonCard} onPress={() => navigation.navigate('LessonDetail', { id: item.id })}>
            <Text style={styles.lessonTitle}>{item.title}</Text>
          </TouchableOpacity>
        )}
        ListEmptyComponent={<Text style={{ textAlign: 'center', marginTop: 16 }}>Ders bulunamadı.</Text>}
        scrollEnabled={false}
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', padding: 16 },
  image: { width: '100%', height: 180, borderRadius: 8, marginBottom: 12 },
  title: { fontSize: 22, fontWeight: 'bold', color: '#222', marginBottom: 8 },
  desc: { fontSize: 15, color: '#555', marginBottom: 8 },
  meta: { fontSize: 13, color: '#888', marginBottom: 16 },
  section: { fontSize: 18, fontWeight: 'bold', marginVertical: 12 },
  lessonCard: { backgroundColor: '#f1f3f4', borderRadius: 8, padding: 12, marginBottom: 8 },
  lessonTitle: { fontSize: 16, color: '#333' },
});

export default CourseDetailScreen; 