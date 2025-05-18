import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Paper,
  Typography,
  Grid,
  Button,
  CircularProgress,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Box
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Print as PrintIcon
} from '@mui/icons-material';
import apps.accountingService from '../../services/accountingService';

interface InvoiceItem {
  id: number;
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

const InvoiceDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
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

  const handleDelete = async () => {
    if (window.confirm('Bu faturayı silmek istediğinizden emin misiniz?')) {
      try {
        await accountingService.deleteInvoice(Number(id));
        navigate('/accounting/invoices');
      } catch (err) {
        setError('Fatura silinirken bir hata oluştu.');
        console.error('Fatura silme hatası:', err);
      }
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: 'TRY'
    }).format(amount);
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
          onClick={() => navigate('/accounting/invoices')}
        >
          Geri Dön
        </Button>
        <Box>
          <Button
            startIcon={<EditIcon />}
            onClick={() => navigate(`/accounting/invoices/${id}/edit`)}
            sx={{ mr: 1 }}
          >
            Düzenle
          </Button>
          <Button
            startIcon={<PrintIcon />}
            onClick={() => window.print()}
            sx={{ mr: 1 }}
          >
            Yazdır
          </Button>
          <Button
            startIcon={<DeleteIcon />}
            color="error"
            onClick={handleDelete}
          >
            Sil
          </Button>
        </Box>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Fatura Bilgileri
            </Typography>
            <Typography>
              <strong>Fatura No:</strong> {invoice.invoice_number}
            </Typography>
            <Typography>
              <strong>Tarih:</strong> {formatDate(invoice.date)}
            </Typography>
            <Typography>
              <strong>Vade Tarihi:</strong> {formatDate(invoice.due_date)}
            </Typography>
            <Typography>
              <strong>Durum:</strong> {invoice.status}
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Müşteri Bilgileri
            </Typography>
            <Typography>
              <strong>Müşteri:</strong> {invoice.customer_name}
            </Typography>
            <Typography>
              <strong>Vergi No:</strong> {invoice.customer_tax_number}
            </Typography>
            <Typography>
              <strong>Adres:</strong> {invoice.customer_address}
            </Typography>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Açıklama</TableCell>
                <TableCell align="right">Miktar</TableCell>
                <TableCell align="right">Birim Fiyat</TableCell>
                <TableCell align="right">KDV Oranı</TableCell>
                <TableCell align="right">Toplam</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {invoice.items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.description}</TableCell>
                  <TableCell align="right">{item.quantity}</TableCell>
                  <TableCell align="right">{formatCurrency(item.unit_price)}</TableCell>
                  <TableCell align="right">%{item.tax_rate}</TableCell>
                  <TableCell align="right">{formatCurrency(item.total)}</TableCell>
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
                  {formatCurrency(invoice.subtotal)}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>
                  <strong>KDV Toplam</strong>
                </TableCell>
                <TableCell align="right">
                  {formatCurrency(invoice.tax_total)}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>
                  <strong>Genel Toplam</strong>
                </TableCell>
                <TableCell align="right">
                  <strong>{formatCurrency(invoice.total)}</strong>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </Box>

        {invoice.notes && (
          <>
            <Divider sx={{ my: 3 }} />
            <Typography variant="h6" gutterBottom>
              Notlar
            </Typography>
            <Typography>
              {invoice.notes}
            </Typography>
          </>
        )}
      </Paper>
    </div>
  );
};

export default InvoiceDetail; 