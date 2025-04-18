import React from 'react';
import { styled } from '@mui/material/styles';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const Root = styled('div')({
  flexGrow: 1,
});

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  textAlign: 'center',
  color: theme.palette.text.secondary,
}));

const StyledCard = styled(Card)({
  minHeight: 200,
});

const data = [
  { name: 'Ocak', muhasebe: 4000, sanal: 2400, egitim: 2400 },
  { name: 'Şubat', muhasebe: 3000, sanal: 1398, egitim: 2210 },
  { name: 'Mart', muhasebe: 2000, sanal: 9800, egitim: 2290 },
  { name: 'Nisan', muhasebe: 2780, sanal: 3908, egitim: 2008 },
  { name: 'Mayıs', muhasebe: 1890, sanal: 4800, egitim: 2181 },
  { name: 'Haziran', muhasebe: 2390, sanal: 3800, egitim: 2500 },
];

const Dashboard: React.FC = () => {
  return (
    <Root>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h4" gutterBottom>
            Hoş Geldiniz
          </Typography>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <StyledCard>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Muhasebe İşlemleri
              </Typography>
              <Typography variant="h4">150</Typography>
              <Typography color="textSecondary">
                Bu ay yapılan işlem sayısı
              </Typography>
            </CardContent>
          </StyledCard>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <StyledCard>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Sanal Şirketler
              </Typography>
              <Typography variant="h4">25</Typography>
              <Typography color="textSecondary">
                Aktif sanal şirket sayısı
              </Typography>
            </CardContent>
          </StyledCard>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <StyledCard>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Eğitim Katılımcıları
              </Typography>
              <Typography variant="h4">500</Typography>
              <Typography color="textSecondary">
                Toplam katılımcı sayısı
              </Typography>
            </CardContent>
          </StyledCard>
        </Grid>

        <Grid item xs={12}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Aylık Aktivite Grafiği
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={data}
                margin={{
                  top: 20,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="muhasebe" fill="#8884d8" name="Muhasebe" />
                <Bar dataKey="sanal" fill="#82ca9d" name="Sanal Şirket" />
                <Bar dataKey="egitim" fill="#ffc658" name="Eğitim" />
              </BarChart>
            </ResponsiveContainer>
          </StyledPaper>
        </Grid>
      </Grid>
    </Root>
  );
};

export default Dashboard; 