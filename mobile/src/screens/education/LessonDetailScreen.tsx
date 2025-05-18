import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, StyleSheet, ScrollView } from 'react-native';
import { educationService } from '../../services/api';
import { Lesson } from '../../types';
import { useRoute } from '@react-navigation/native';

const LessonDetailScreen = () => {
  const route = useRoute<any>();
  const { id } = route.params;
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    educationService.getLesson(id).then(setLesson).finally(() => setLoading(false));
  }, [id]);

  if (loading || !lesson) {
    return <ActivityIndicator style={{ flex: 1 }} size="large" color="#007bff" />;
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>{lesson.title}</Text>
      <Text style={styles.content}>{lesson.content}</Text>
      {lesson.video_url && (
        <View style={styles.videoContainer}>
          {/* Video oynatıcı entegre edilebilir */}
          <Text style={styles.videoLabel}>Video:</Text>
          <Text style={styles.videoUrl}>{lesson.video_url}</Text>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', padding: 16 },
  title: { fontSize: 22, fontWeight: 'bold', color: '#222', marginBottom: 12 },
  content: { fontSize: 15, color: '#555', marginBottom: 16 },
  videoContainer: { marginTop: 16, backgroundColor: '#f1f3f4', borderRadius: 8, padding: 12 },
  videoLabel: { fontWeight: 'bold', color: '#333' },
  videoUrl: { color: '#007bff' },
});

export default LessonDetailScreen; 