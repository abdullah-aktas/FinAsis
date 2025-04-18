import React from 'react';
import { styled } from '@mui/material/styles';
import {
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  AccountBalance as AccountingIcon,
  Business as CompanyIcon,
  School as EducationIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const drawerWidth = 240;

const Root = styled('div')({
  display: 'flex',
});

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  zIndex: theme.zIndex.drawer + 1,
}));

const StyledDrawer = styled('nav')(({ theme }) => ({
  width: drawerWidth,
  flexShrink: 0,
  '& .MuiDrawer-paper': {
    width: drawerWidth,
    boxSizing: 'border-box',
  },
}));

const Main = styled('main')(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
}));

const ToolbarSpacer = styled('div')(({ theme }) => theme.mixins.toolbar);

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Muhasebe', icon: <AccountingIcon />, path: '/accounting' },
    { text: 'Sanal Şirket', icon: <CompanyIcon />, path: '/virtual-company' },
    { text: 'Eğitim', icon: <EducationIcon />, path: '/education' },
  ];

  const drawer = (
    <div>
      <ToolbarSpacer />
      <List>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.text}
            onClick={() => {
              navigate(item.path);
              setMobileOpen(false);
            }}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <Root>
      <StyledAppBar position="fixed">
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setMobileOpen(!mobileOpen)}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            FinAsis
          </Typography>
        </Toolbar>
      </StyledAppBar>
      <StyledDrawer>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
          }}
          open
        >
          {drawer}
        </Drawer>
      </StyledDrawer>
      <Main>
        <ToolbarSpacer />
        {children}
      </Main>
    </Root>
  );
};

export default Layout; 