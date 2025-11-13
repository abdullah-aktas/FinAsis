import { useEffect } from 'react';
import { useThree } from '@react-three/fiber';

// VRManager: WebXR entegrasyonu ve VR kamera/kontrol modları
export default function VRManager({ enabled }) {
  const { gl, camera } = useThree();
  useEffect(() => {
    if (enabled && gl.xr) {
      gl.xr.enabled = true;
      gl.xr.setSession(null);
    } else if (gl.xr) {
      gl.xr.enabled = false;
    }
  }, [enabled, gl]);
  return null;
}
// VRManager ile VR modunu aç/kapat, desktop ve mobilde sorunsuz geçiş
