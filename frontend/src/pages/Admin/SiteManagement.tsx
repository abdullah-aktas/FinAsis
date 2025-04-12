import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Grid,
  Tabs,
  Tab,
  Box,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  Save as SaveIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import adminService from '../../services/adminService';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      aria-labelledby={`admin-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined: string;
  last_login: string;
}

interface SystemSettings {
  site_name: string;
  site_description: string;
  contact_email: string;
  enable_registration: boolean;
  maintenance_mode: boolean;
  default_currency: string;
  default_language: string;
  invoice_prefix: string;
  invoice_start_number: number;
  tax_rates: string;
}

const SiteManagement: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [users, setUsers] = useState<User[]>([]);
  const [settings, setSettings] = useState<SystemSettings>({
    site_name: '',
    site_description: '',
    contact_email: '',
    enable_registration: true,
    maintenance_mode: false,
    default_currency: 'TRY',
    default_language: 'tr',
    invoice_prefix: 'INV',
    invoice_start_number: 1000,
    tax_rates: '0,1,8,18'
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [openUserDialog, setOpenUserDialog] = useState<boolean>(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [newUser, setNewUser] = useState<Partial<User>>({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    is_active: true,
    is_staff: false,
    is_superuser: false
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [usersResponse, settingsResponse] = await Promise.all([
        adminService.getUsers(),
        adminService.getSystemSettings()
      ]);
      setUsers(usersResponse.data);
      setSettings(settingsResponse.data);
      setError(null);
    } catch (err) {
      setError('Veriler yüklenirken bir hata oluştu.');
      console.error('Veri yükleme hatası:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleSettingChange = (field: string, value: any) => {
    setSettings({
      ...settings,
      [field]: value
    });
  };

  const handleSaveSettings = async () => {
    try {
      setSaving(true);
      await adminService.updateSystemSettings(settings);
      setSuccess('Ayarlar başarıyla kaydedildi.');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Ayarlar kaydedilirken bir hata oluştu.');
      console.error('Ayar kaydetme hatası:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleOpenUserDialog = (user?: User) => {
    if (user) {
      setCurrentUser(user);
      setNewUser({
        username: user.username,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        is_active: user.is_active,
        is_staff: user.is_staff,
        is_superuser: user.is_superuser
      });
    } else {
      setCurrentUser(null);
      setNewUser({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        is_active: true,
        is_staff: false,
        is_superuser: false
      });
    }
    setOpenUserDialog(true);
  };

  const handleCloseUserDialog = () => {
    setOpenUserDialog(false);
    setCurrentUser(null);
    setNewUser({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      is_active: true,
      is_staff: false,
      is_superuser: false
    });
  };

  const handleUserChange = (field: string, value: any) => {
    setNewUser({
      ...newUser,
      [field]: value
    });
  };

  const handleSaveUser = async () => {
    try {
      setSaving(true);
      if (currentUser) {
        await adminService.updateUser(currentUser.id, newUser);
        setSuccess('Kullanıcı başarıyla güncellendi.');
      } else {
        await adminService.createUser(newUser);
        setSuccess('Kullanıcı başarıyla oluşturuldu.');
      }
      fetchData();
      handleCloseUserDialog();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Kullanıcı kaydedilirken bir hata oluştu.');
      console.error('Kullanıcı kaydetme hatası:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (window.confirm('Bu kullanıcıyı silmek istediğinizden emin misiniz?')) {
      try {
        setSaving(true);
        await adminService.deleteUser(userId);
        setSuccess('Kullanıcı başarıyla silindi.');
        fetchData();
        setTimeout(() => setSuccess(null), 3000);
      } catch (err) {
        setError('Kullanıcı silinirken bir hata oluştu.');
        console.error('Kullanıcı silme hatası:', err);
      } finally {
        setSaving(false);
      }
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR');
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '2rem' }}>
        <CircularProgress />
      </div>
    );
  }

  return (
    <div>
      <Typography variant="h4" gutterBottom>
        Site Yönetimi
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Genel Ayarlar" />
          <Tab label="Kullanıcı Yönetimi" />
          <Tab label="Sistem Bakımı" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Site Bilgileri
              </Typography>
              <TextField
                fullWidth
                label="Site Adı"
                value={settings.site_name}
                onChange={(e) => handleSettingChange('site_name', e.target.value)}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Site Açıklaması"
                value={settings.site_description}
                onChange={(e) => handleSettingChange('site_description', e.target.value)}
                margin="normal"
                multiline
                rows={3}
              />
              <TextField
                fullWidth
                label="İletişim E-posta"
                value={settings.contact_email}
                onChange={(e) => handleSettingChange('contact_email', e.target.value)}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Sistem Ayarları
              </Typography>
              <FormControl fullWidth margin="normal">
                <InputLabel>Varsayılan Para Birimi</InputLabel>
                <Select
                  value={settings.default_currency}
                  onChange={(e) => handleSettingChange('default_currency', e.target.value)}
                  label="Varsayılan Para Birimi"
                >
                  <MenuItem value="TRY">Türk Lirası (TRY)</MenuItem>
                  <MenuItem value="USD">Amerikan Doları (USD)</MenuItem>
                  <MenuItem value="EUR">Euro (EUR)</MenuItem>
                  <MenuItem value="GBP">İngiliz Sterlini (GBP)</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth margin="normal">
                <InputLabel>Varsayılan Dil</InputLabel>
                <Select
                  value={settings.default_language}
                  onChange={(e) => handleSettingChange('default_language', e.target.value)}
                  label="Varsayılan Dil"
                >
                  <MenuItem value="tr">Türkçe</MenuItem>
                  <MenuItem value="en">İngilizce</MenuItem>
                </Select>
              </FormControl>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enable_registration}
                    onChange={(e) => handleSettingChange('enable_registration', e.target.checked)}
                  />
                }
                label="Kullanıcı Kaydına İzin Ver"
                sx={{ mt: 2 }}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.maintenance_mode}
                    onChange={(e) => handleSettingChange('maintenance_mode', e.target.checked)}
                  />
                }
                label="Bakım Modu"
                sx={{ mt: 1 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Fatura Ayarları
              </Typography>
              <TextField
                fullWidth
                label="Fatura Öneki"
                value={settings.invoice_prefix}
                onChange={(e) => handleSettingChange('invoice_prefix', e.target.value)}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Fatura Başlangıç Numarası"
                type="number"
                value={settings.invoice_start_number}
                onChange={(e) => handleSettingChange('invoice_start_number', Number(e.target.value))}
                margin="normal"
                inputProps={{ min: 1 }}
              />
              <TextField
                fullWidth
                label="KDV Oranları (virgülle ayırın)"
                value={settings.tax_rates}
                onChange={(e) => handleSettingChange('tax_rates', e.target.value)}
                margin="normal"
                helperText="Örnek: 0,1,8,18"
              />
            </Grid>
          </Grid>
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<SaveIcon />}
              onClick={handleSaveSettings}
              disabled={saving}
            >
              {saving ? 'Kaydediliyor...' : 'Ayarları Kaydet'}
            </Button>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Kullanıcı Listesi
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={() => handleOpenUserDialog()}
            >
              Yeni Kullanıcı
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Kullanıcı Adı</TableCell>
                  <TableCell>Ad Soyad</TableCell>
                  <TableCell>E-posta</TableCell>
                  <TableCell>Durum</TableCell>
                  <TableCell>Yetki</TableCell>
                  <TableCell>Kayıt Tarihi</TableCell>
                  <TableCell>Son Giriş</TableCell>
                  <TableCell align="center">İşlemler</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{`${user.first_name} ${user.last_name}`}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      {user.is_active ? 'Aktif' : 'Pasif'}
                    </TableCell>
                    <TableCell>
                      {user.is_superuser ? 'Süper Kullanıcı' : user.is_staff ? 'Yönetici' : 'Kullanıcı'}
                    </TableCell>
                    <TableCell>{formatDate(user.date_joined)}</TableCell>
                    <TableCell>{user.last_login ? formatDate(user.last_login) : '-'}</TableCell>
                    <TableCell align="center">
                      <IconButton
                        color="primary"
                        onClick={() => handleOpenUserDialog(user)}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        color="error"
                        onClick={() => handleDeleteUser(user.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            Sistem Bakım İşlemleri
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Veritabanı Yedekleme
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Veritabanının tam bir yedeğini alır. Bu işlem biraz zaman alabilir.
                </Typography>
                <Button
                  variant="outlined"
                  color="primary"
                  startIcon={<SaveIcon />}
                  onClick={() => alert('Yedekleme işlemi başlatıldı.')}
                >
                  Yedekleme Başlat
                </Button>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Önbellek Temizleme
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Sistem önbelleğini temizler ve yeniden oluşturur. Performans sorunlarında faydalı olabilir.
                </Typography>
                <Button
                  variant="outlined"
                  color="primary"
                  startIcon={<RefreshIcon />}
                  onClick={() => alert('Önbellek temizleme işlemi başlatıldı.')}
                >
                  Önbelleği Temizle
                </Button>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Log Dosyaları
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Sistem log dosyalarını görüntüler ve indirir. Sorun giderme için kullanılır.
                </Typography>
                <Button
                  variant="outlined"
                  color="primary"
                  onClick={() => alert('Log dosyaları indiriliyor.')}
                >
                  Log Dosyalarını İndir
                </Button>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Sistem Durumu
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Sistem kaynaklarının kullanımını ve performansını gösterir.
                </Typography>
                <Button
                  variant="outlined"
                  color="primary"
                  onClick={() => alert('Sistem durumu kontrol ediliyor.')}
                >
                  Durumu Kontrol Et
                </Button>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>

      <Dialog open={openUserDialog} onClose={handleCloseUserDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {currentUser ? 'Kullanıcı Düzenle' : 'Yeni Kullanıcı'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Kullanıcı Adı"
                value={newUser.username}
                onChange={(e) => handleUserChange('username', e.target.value)}
                margin="normal"
                required
                disabled={!!currentUser}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="E-posta"
                value={newUser.email}
                onChange={(e) => handleUserChange('email', e.target.value)}
                margin="normal"
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Ad"
                value={newUser.first_name}
                onChange={(e) => handleUserChange('first_name', e.target.value)}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Soyad"
                value={newUser.last_name}
                onChange={(e) => handleUserChange('last_name', e.target.value)}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={newUser.is_active}
                    onChange={(e) => handleUserChange('is_active', e.target.checked)}
                  />
                }
                label="Aktif"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={newUser.is_staff}
                    onChange={(e) => handleUserChange('is_staff', e.target.checked)}
                  />
                }
                label="Yönetici Yetkisi"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={newUser.is_superuser}
                    onChange={(e) => handleUserChange('is_superuser', e.target.checked)}
                  />
                }
                label="Süper Kullanıcı"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseUserDialog}>İptal</Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleSaveUser}
            disabled={saving}
          >
            {saving ? 'Kaydediliyor...' : 'Kaydet'}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default SiteManagement; 