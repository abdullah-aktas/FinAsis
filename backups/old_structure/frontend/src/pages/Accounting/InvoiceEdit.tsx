import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
import apps.accountingService from '../../services/accountingService';

interface InvoiceItem {
  id?: number;
  description: string;
  quantity: number;
  unit_price: number;
  tax_rate: number;
  total: number;
}

interface Invoice {
  id: number;
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

const InvoiceEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchInvoice();
  }, [id]);

  const fetchInvoice = async () => {
    try {
      setLoading(true);
      const response = await accountingService.getInvoice(Number(id));
      setInvoice(response.data);
      setError(null);
    } catch (err) {
      setError('Fatura yüklenirken bir hata oluştu.');
      console.error('Fatura yükleme hatası:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: any) => {
    if (invoice) {
      setInvoice({
        ...invoice,
        [field]: value
      });
    }
  };

  const handleItemChange = (index: number, field: string, value: any) => {
    if (invoice) {
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
    }
  };

  const addItem = () => {
    if (invoice) {
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
    }
  };

  const removeItem = (index: number) => {
    if (invoice) {
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
    }
  };

  const handleSave = async () => {
    if (invoice) {
      try {
        setSaving(true);
        await accountingService.updateInvoice(Number(id), invoice);
        navigate(`/accounting/invoices/${id}`);
      } catch (err) {
        setError('Fatura kaydedilirken bir hata oluştu.');
        console.error('Fatura kaydetme hatası:', err);
      } finally {
        setSaving(false);
      }
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '2rem' }}>
        <CircularProgress />
      </div>
    );
  }

  if (error) {
    return (
      <Typography color="error" style={{ marginTop: '1rem' }}>
        {error}
      </Typography>
    );
  }

  if (!invoice) {
    return (
      <Typography>
        Fatura bulunamadı.
      </Typography>
    );
  }

  return (
    <div>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(`/accounting/invoices/${id}`)}
        >
          Geri Dön
        </Button>
        <Button
          variant="contained"
          color="primary"
          startIcon={<SaveIcon />}
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Kaydediliyor...' : 'Kaydet'}
        </Button>
      </Box>

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
            />
            <TextField
              fullWidth
              label="Tarih"
              type="date"
              value={invoice.date.split('T')[0]}
              onChange={(e) => handleChange('date', e.target.value)}
              margin="normal"
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              fullWidth
              label="Vade Tarihi"
              type="date"
              value={invoice.due_date.split('T')[0]}
              onChange={(e) => handleChange('due_date', e.target.value)}
              margin="normal"
              InputLabelProps={{ shrink: true }}
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
                    />
                  </TableCell>
                  <TableCell align="right">
                    <TextField
                      type="number"
                      value={item.quantity}
                      onChange={(e) => handleItemChange(index, 'quantity', Number(e.target.value))}
                      size="small"
                      inputProps={{ min: 0, step: 1 }}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <TextField
                      type="number"
                      value={item.unit_price}
                      onChange={(e) => handleItemChange(index, 'unit_price', Number(e.target.value))}
                      size="small"
                      inputProps={{ min: 0, step: 0.01 }}
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

export default InvoiceEdit; 