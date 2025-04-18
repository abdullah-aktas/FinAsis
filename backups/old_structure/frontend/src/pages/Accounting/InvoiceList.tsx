import React, { useState, useEffect } from 'react';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper, 
  Button, 
  Typography, 
  CircularProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  Add as AddIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon,
  Visibility as ViewIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import apps.accountingService from '../../services/accountingService';

interface Invoice {
  id: number;
  invoice_number: string;
  date: string;
  due_date: string;
  customer_name: string;
  total: number;
  status: string;
}

const InvoiceList: React.FC = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const response = await accountingService.getInvoices();
      setInvoices(response.data);
      setError(null);
    } catch (err) {
      setError('Faturalar yüklenirken bir hata oluştu.');
      console.error('Fatura yükleme hatası:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Bu faturayı silmek istediğinizden emin misiniz?')) {
      try {
        await accountingService.deleteInvoice(id);
        setInvoices(invoices.filter(invoice => invoice.id !== id));
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

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <Typography variant="h5" component="h2">
          Faturalar
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => navigate('/accounting/invoices/new')}
        >
          Yeni Fatura
        </Button>
      </div>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Fatura No</TableCell>
              <TableCell>Tarih</TableCell>
              <TableCell>Vade Tarihi</TableCell>
              <TableCell>Müşteri</TableCell>
              <TableCell align="right">Tutar</TableCell>
              <TableCell>Durum</TableCell>
              <TableCell align="center">İşlemler</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {invoices.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Henüz fatura bulunmamaktadır.
                </TableCell>
              </TableRow>
            ) : (
              invoices.map((invoice) => (
                <TableRow key={invoice.id}>
                  <TableCell>{invoice.invoice_number}</TableCell>
                  <TableCell>{formatDate(invoice.date)}</TableCell>
                  <TableCell>{formatDate(invoice.due_date)}</TableCell>
                  <TableCell>{invoice.customer_name}</TableCell>
                  <TableCell align="right">{formatCurrency(invoice.total)}</TableCell>
                  <TableCell>{invoice.status}</TableCell>
                  <TableCell align="center">
                    <Tooltip title="Görüntüle">
                      <IconButton 
                        size="small" 
                        onClick={() => navigate(`/accounting/invoices/${invoice.id}`)}
                      >
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Düzenle">
                      <IconButton 
                        size="small" 
                        onClick={() => navigate(`/accounting/invoices/${invoice.id}/edit`)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Sil">
                      <IconButton 
                        size="small" 
                        onClick={() => handleDelete(invoice.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};

export default InvoiceList; 