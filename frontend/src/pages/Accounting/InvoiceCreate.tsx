import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  CircularProgress,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Box,
  IconButton,
  MenuItem,
  FormControl,
  InputLabel,
  Select
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import accountingService from '../../services/accountingService';

interface InvoiceItem {
  description: string;
  quantity: number;
  unit_price: number;
  tax_rate: number;
  total: number;
}

interface Invoice {
  invoice_number: string;
  date: string;
  due_date: string;
  customer_name: string;
  customer_tax_number: string;
  customer_address: string;
  items: InvoiceItem[];
  subtotal: number;
  tax_total: number;
  total: number;
  status: string;
  notes: string;
}

const InvoiceCreate: React.FC = () => {
  const navigate = useNavigate();
  const [invoice, setInvoice] = useState<Invoice>({
    invoice_number: '',
    date: new Date().toISOString().split('T')[0],
    due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    customer_name: '',
    customer_tax_number: '',
    customer_address: '',
    items: [],
    subtotal: 0,
    tax_total: 0,
    total: 0,
    status: 'draft',
    notes: ''
  });
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (field: string, value: any) => {
    setInvoice({
      ...invoice,
      [field]: value
    });
  };

  const handleItemChange = (index: number, field: string, value: any) => {
    const updatedItems = [...invoice.items];
    updatedItems[index] = {
      ...updatedItems[index],
      [field]: value
    };
    
    // Toplam tutarı hesapla
    updatedItems[index].total = 
      updatedItems[index].quantity * 
      updatedItems[index].unit_price * 
      (1 + updatedItems[index].tax_rate / 100);
    
    // Fatura toplamlarını güncelle
    const subtotal = updatedItems.reduce((sum, item) => sum + item.total, 0);
    const taxTotal = updatedItems.reduce((sum, item) => 
      sum + (item.total * item.tax_rate / (100 + item.tax_rate)), 0);
    
    setInvoice({
      ...invoice,
      items: updatedItems,
      subtotal: subtotal,
      tax_total: taxTotal,
      total: subtotal
    });
  };

  const addItem = () => {
    const newItem: InvoiceItem = {
      description: '',
      quantity: 1,
      unit_price: 0,
      tax_rate: 18,
      total: 0
    };
    
    setInvoice({
      ...invoice,
      items: [...invoice.items, newItem]
    });
  };

  const removeItem = (index: number) => {
    const updatedItems = invoice.items.filter((_, i) => i !== index);
    
    // Fatura toplamlarını güncelle
    const subtotal = updatedItems.reduce((sum, item) => sum + item.total, 0);
    const taxTotal = updatedItems.reduce((sum, item) => 
      sum + (item.total * item.tax_rate / (100 + item.tax_rate)), 0);
    
    setInvoice({
      ...invoice,
      items: updatedItems,
      subtotal: subtotal,
      tax_total: taxTotal,
      total: subtotal
    });
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await accountingService.createInvoice(invoice);
      navigate(`/accounting/invoices/${response.data.id}`);
    } catch (err) {
      setError('Fatura kaydedilirken bir hata oluştu.');
      console.error('Fatura kaydetme hatası:', err);
    } finally {
      setSaving(false);
    }
  };

  const validateInvoice = (): boolean => {
    if (!invoice.invoice_number) {
      setError('Fatura numarası gereklidir.');
      return false;
    }
    
    if (!invoice.customer_name) {
      setError('Müşteri adı gereklidir.');
      return false;
    }
    
    if (invoice.items.length === 0) {
      setError('En az bir fatura kalemi eklemelisiniz.');
      return false;
    }
    
    for (let i = 0; i < invoice.items.length; i++) {
      const item = invoice.items[i];
      if (!item.description) {
        setError(`${i + 1}. kalem için açıklama gereklidir.`);
        return false;
      }
      if (item.quantity <= 0) {
        setError(`${i + 1}. kalem için miktar 0\'dan büyük olmalıdır.`);
        return false;
      }
      if (item.unit_price <= 0) {
        setError(`${i + 1}. kalem için birim fiyat 0\'dan büyük olmalıdır.`);
        return false;
      }
    }
    
    return true;
  };

  const handleSubmit = () => {
    if (validateInvoice()) {
      handleSave();
    }
  };

  return (
    <div>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/accounting/invoices')}
        >
          Geri Dön
        </Button>
        <Button
          variant="contained"
          color="primary"
          startIcon={<SaveIcon />}
          onClick={handleSubmit}
          disabled={saving}
        >
          {saving ? 'Kaydediliyor...' : 'Kaydet'}
        </Button>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      <Paper sx={{ p: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Fatura Bilgileri
            </Typography>
            <TextField
              fullWidth
              label="Fatura No"
              value={invoice.invoice_number}
              onChange={(e) => handleChange('invoice_number', e.target.value)}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Tarih"
              type="date"
              value={invoice.date}
              onChange={(e) => handleChange('date', e.target.value)}
              margin="normal"
              InputLabelProps={{ shrink: true }}
              required
            />
            <TextField
              fullWidth
              label="Vade Tarihi"
              type="date"
              value={invoice.due_date}
              onChange={(e) => handleChange('due_date', e.target.value)}
              margin="normal"
              InputLabelProps={{ shrink: true }}
              required
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Durum</InputLabel>
              <Select
                value={invoice.status}
                onChange={(e) => handleChange('status', e.target.value)}
                label="Durum"
              >
                <MenuItem value="draft">Taslak</MenuItem>
                <MenuItem value="sent">Gönderildi</MenuItem>
                <MenuItem value="paid">Ödendi</MenuItem>
                <MenuItem value="cancelled">İptal Edildi</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Müşteri Bilgileri
            </Typography>
            <TextField
              fullWidth
              label="Müşteri Adı"
              value={invoice.customer_name}
              onChange={(e) => handleChange('customer_name', e.target.value)}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Vergi Numarası"
              value={invoice.customer_tax_number}
              onChange={(e) => handleChange('customer_tax_number', e.target.value)}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Adres"
              value={invoice.customer_address}
              onChange={(e) => handleChange('customer_address', e.target.value)}
              margin="normal"
              multiline
              rows={3}
            />
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Fatura Kalemleri
          </Typography>
          <Button
            startIcon={<AddIcon />}
            onClick={addItem}
          >
            Kalem Ekle
          </Button>
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Açıklama</TableCell>
                <TableCell align="right">Miktar</TableCell>
                <TableCell align="right">Birim Fiyat</TableCell>
                <TableCell align="right">KDV Oranı (%)</TableCell>
                <TableCell align="right">Toplam</TableCell>
                <TableCell align="center">İşlem</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {invoice.items.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <TextField
                      fullWidth
                      value={item.description}
                      onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                      size="small"
                      required
                    />
                  </TableCell>
                  <TableCell align="right">
                    <TextField
                      type="number"
                      value={item.quantity}
                      onChange={(e) => handleItemChange(index, 'quantity', Number(e.target.value))}
                      size="small"
                      inputProps={{ min: 0, step: 1 }}
                      required
                    />
                  </TableCell>
                  <TableCell align="right">
                    <TextField
                      type="number"
                      value={item.unit_price}
                      onChange={(e) => handleItemChange(index, 'unit_price', Number(e.target.value))}
                      size="small"
                      inputProps={{ min: 0, step: 0.01 }}
                      required
                    />
                  </TableCell>
                  <TableCell align="right">
                    <TextField
                      type="number"
                      value={item.tax_rate}
                      onChange={(e) => handleItemChange(index, 'tax_rate', Number(e.target.value))}
                      size="small"
                      inputProps={{ min: 0, step: 1 }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    {new Intl.NumberFormat('tr-TR', {
                      style: 'currency',
                      currency: 'TRY'
                    }).format(item.total)}
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      color="error"
                      onClick={() => removeItem(index)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {invoice.items.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" color="textSecondary">
                      Henüz fatura kalemi eklenmemiş. "Kalem Ekle" butonuna tıklayarak ekleyebilirsiniz.
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Table>
            <TableBody>
              <TableRow>
                <TableCell>
                  <strong>Ara Toplam</strong>
                </TableCell>
                <TableCell align="right">
                  {new Intl.NumberFormat('tr-TR', {
                    style: 'currency',
                    currency: 'TRY'
                  }).format(invoice.subtotal)}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>
                  <strong>KDV Toplam</strong>
                </TableCell>
                <TableCell align="right">
                  {new Intl.NumberFormat('tr-TR', {
                    style: 'currency',
                    currency: 'TRY'
                  }).format(invoice.tax_total)}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>
                  <strong>Genel Toplam</strong>
                </TableCell>
                <TableCell align="right">
                  <strong>
                    {new Intl.NumberFormat('tr-TR', {
                      style: 'currency',
                      currency: 'TRY'
                    }).format(invoice.total)}
                  </strong>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </Box>

        <Divider sx={{ my: 3 }} />
        
        <TextField
          fullWidth
          label="Notlar"
          value={invoice.notes}
          onChange={(e) => handleChange('notes', e.target.value)}
          margin="normal"
          multiline
          rows={3}
        />
      </Paper>
    </div>
  );
};

export default InvoiceCreate; 