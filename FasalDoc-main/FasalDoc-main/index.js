import 'react-native-get-random-values';
import { AppRegistry } from 'react-native';
import App from './src/App';
import { name as appName } from './app.json';

// appName must match getMainComponentName() in MainActivity.kt
AppRegistry.registerComponent(appName, () => App);
