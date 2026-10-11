import { createTheme, alpha } from '@mui/material/styles';

const PRIMARY = '#4F46E5';
const SUCCESS = '#16A34A';
const WARNING = '#D97706';
const ERROR = '#DC2626';
const BORDER = '#EAECEF';

export const theme = createTheme({
  palette: {
    mode: 'light',
    background: { default: '#F7F8FA', paper: '#FFFFFF' },
    primary: { main: PRIMARY },
    success: { main: SUCCESS },
    warning: { main: WARNING },
    error: { main: ERROR },
    text: { primary: '#0F172A', secondary: '#64748B' },
    divider: BORDER,
  },
  shape: { borderRadius: 14 },
  typography: {
    fontFamily:
      'Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    h1: { fontWeight: 700, letterSpacing: '-0.02em' },
    h2: { fontWeight: 700, letterSpacing: '-0.02em' },
    h3: { fontWeight: 700, letterSpacing: '-0.02em' },
    h4: { fontWeight: 700, letterSpacing: '-0.01em' },
    h5: { fontWeight: 600, letterSpacing: '-0.01em' },
    h6: { fontWeight: 600, letterSpacing: '-0.01em' },
    subtitle2: { fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' },
    button: { textTransform: 'none', fontWeight: 600 },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#F7F8FA',
          WebkitFontSmoothing: 'antialiased',
          fontFeatureSettings: '"tnum" 1, "cv11" 1',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
      },
    },
    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          border: `1px solid ${BORDER}`,
          borderRadius: 14,
          backgroundImage: 'none',
          boxShadow: '0 1px 2px rgba(15, 23, 42, 0.02)',
        },
      },
    },
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: { borderRadius: 10, paddingInline: 16 },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          backgroundColor: '#FFFFFF',
        },
        notchedOutline: { borderColor: BORDER },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: '#0F172A',
          fontSize: 12,
          borderRadius: 8,
          padding: '8px 10px',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontWeight: 600, borderRadius: 8 },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          marginInline: 8,
          '&.Mui-selected': {
            backgroundColor: alpha(PRIMARY, 0.08),
            color: PRIMARY,
            '& .MuiListItemIcon-root': { color: PRIMARY },
            '&:hover': { backgroundColor: alpha(PRIMARY, 0.12) },
          },
        },
      },
    },
  },
});