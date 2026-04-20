import { Platform, TextStyle } from 'react-native';

const fontFamily = Platform.select({
  ios: 'System',
  android: 'Roboto',
  default: 'System',
});

export const Fonts = {
  heading: {
    fontFamily,
    fontSize: 18,
    fontWeight: '500' as TextStyle['fontWeight'],
    lineHeight: 26,
  },
  subheading: {
    fontFamily,
    fontSize: 15,
    fontWeight: '500' as TextStyle['fontWeight'],
    lineHeight: 22,
  },
  body: {
    fontFamily,
    fontSize: 14,
    fontWeight: '400' as TextStyle['fontWeight'],
    lineHeight: 22,
  },
  caption: {
    fontFamily,
    fontSize: 11,
    fontWeight: '400' as TextStyle['fontWeight'],
    lineHeight: 16,
  },
  label: {
    fontFamily,
    fontSize: 13,
    fontWeight: '500' as TextStyle['fontWeight'],
    lineHeight: 18,
  },
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 24,
  xxxl: 32,
};

export const BorderRadius = {
  sm: 8,
  md: 12,
  pill: 20,
  frame: 24,
};
