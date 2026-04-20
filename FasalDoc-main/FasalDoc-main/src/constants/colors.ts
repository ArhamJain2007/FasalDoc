import { ColorSchemeName } from 'react-native';

export const LightColors = {
  PRIMARY_GREEN: '#1D9E75',
  LIGHT_GREEN: '#E1F5EE',
  DARK_GREEN: '#0F6E56',
  AMBER: '#EF9F27',
  LIGHT_AMBER: '#FAEEDA',
  BLUE: '#378ADD',
  LIGHT_BLUE: '#E6F1FB',
  RED: '#E24B4A',
  LIGHT_RED: '#FCEBEB',
  PURPLE: '#7F77DD',
  LIGHT_PURPLE: '#EEEDFE',
  GRAY_BG: '#F5F5F2',
  CARD_BG: '#FFFFFF',
  TEXT_PRIMARY: '#1A1A18',
  TEXT_SECONDARY: '#6B6B67',
  TEXT_TERTIARY: '#A0A09C',
  BORDER: 'rgba(0,0,0,0.1)',
  WHITE: '#FFFFFF',
  BLACK: '#000000',
  SHADOW: 'rgba(0,0,0,0.08)',
};

export const DarkColors = {
  PRIMARY_GREEN: '#1D9E75',
  LIGHT_GREEN: '#0F3D2E',
  DARK_GREEN: '#9FE1CB',
  AMBER: '#EF9F27',
  LIGHT_AMBER: '#3D2D0A',
  BLUE: '#5BA4E5',
  LIGHT_BLUE: '#0A1F3D',
  RED: '#E24B4A',
  LIGHT_RED: '#3D0F0F',
  PURPLE: '#9F9AE8',
  LIGHT_PURPLE: '#1A183D',
  GRAY_BG: '#121210',
  CARD_BG: '#1E1E1C',
  TEXT_PRIMARY: '#F0F0EC',
  TEXT_SECONDARY: '#9B9B97',
  TEXT_TERTIARY: '#5A5A57',
  BORDER: 'rgba(255,255,255,0.12)',
  WHITE: '#FFFFFF',
  BLACK: '#000000',
  SHADOW: 'rgba(0,0,0,0.4)',
};

export type Colors = typeof LightColors;

export const getColors = (scheme: ColorSchemeName): Colors =>
  scheme === 'dark' ? DarkColors : LightColors;
