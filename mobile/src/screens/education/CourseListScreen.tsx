import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, Image, ActivityIndicator, StyleSheet } from 'react-native';
import { educationService } from '../../services/api';
import { Course } from '../../types';
import { useNavigation } from '@react-navigation/native';

const CourseListScreen = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const navigation = useNavigation();

  useEffect(() => {
    educationService.getCourses()
      .then(setCourses)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <ActivityIndicator style={{ flex: 1 }} size="large" color="#007bff" />;
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={courses}
        keyExtractor={item => item.id.toString()}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.card} onPress={() => navigation.navigate('CourseDetail', { id: item.id })}>
            {item.image && <Image source={{ uri: item.image }} style={styles.image} />}
            <View style={{ flex: 1 }}>
              <Text style={styles.title}>{item.title}</Text>
              <Text style={styles.desc} numberOfLines={2}>{item.description}</Text>
              <Text style={styles.meta}>{item.level} | {item.duration} saat</Text>
            </View>
          </TouchableOpacity>
        )}
        ListEmptyComponent={<Text style={{ textAlign: 'center', marginTop: 32 }}>Kurs bulunamadı.</Text>}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', padding: 16 },
  card: { flexDirection: 'row', backgroundColor: '#f8f9fa', borderRadius: 8, marginBottom: 12, padding: 12, alignItems: 'center', elevation: 2 },
  image: { width: 64, height: 64, borderRadius: 8, marginRight: 12 },
  title: { fontSize: 18, fontWeight: 'bold', color: '#222' },
  desc: { fontSize: 14, color: '#555', marginVertical: 4 },
  meta: { fontSize: 12, color: '#888' },
});

export default CourseListScreen; 