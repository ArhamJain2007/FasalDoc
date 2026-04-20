export type DiseaseClass = {
  id: number;
  label: string;
  cropName: string;
  severity: 'low' | 'medium' | 'high';
  treatmentId: string;
  descriptionKey: string;
};

// 38 class names matching PlantVillage dataset label order
export const DISEASE_CLASSES: DiseaseClass[] = [
  { id: 0, label: 'Apple___Apple_scab', cropName: 'Apple', severity: 'medium', treatmentId: 'T001', descriptionKey: 'apple_scab' },
  { id: 1, label: 'Apple___Black_rot', cropName: 'Apple', severity: 'high', treatmentId: 'T002', descriptionKey: 'apple_black_rot' },
  { id: 2, label: 'Apple___Cedar_apple_rust', cropName: 'Apple', severity: 'medium', treatmentId: 'T003', descriptionKey: 'cedar_apple_rust' },
  { id: 3, label: 'Apple___healthy', cropName: 'Apple', severity: 'low', treatmentId: 'T000', descriptionKey: 'healthy' },
  { id: 4, label: 'Blueberry___healthy', cropName: 'Blueberry', severity: 'low', treatmentId: 'T000', descriptionKey: 'healthy' },
  { id: 5, label: 'Cherry_(including_sour)___Powdery_mildew', cropName: 'Cherry', severity: 'medium', treatmentId: 'T004', descriptionKey: 'powdery_mildew' },
  { id: 6, label: 'Cherry_(including_sour)___healthy', cropName: 'Cherry', severity: 'low', treatmentId: 'T000', descriptionKey: 'healthy' },
  { id: 7, label: 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', cropName: 'Maize', severity: 'medium', treatmentId: 'T005', descriptionKey: 'gray_leaf_spot' },
  { id: 8, label: 'Corn_(maize)___Common_rust_', cropName: 'Maize', severity: 'medium', treatmentId: 'T006', descriptionKey: 'common_rust' },
  { id: 9, label: 'Corn_(maize)___Northern_Leaf_Blight', cropName: 'Maize', severity: 'high', treatmentId: 'T007', descriptionKey: 'northern_leaf_blight' },
  { id: 10, label: 'Corn_(maize)___healthy', cropName: 'Maize', severity: 'low', treatmentId: 'T000', descriptionKey: 'healthy' },
  { id: 11, label: 'Grape___Black_rot', cropName: 'Grape', severity: 'high', treatmentId: 'T008', descriptionKey: 'grape_black_rot' },
  { id: 12, label: 'Grape___Esca_(Black_Measles)', cropName: 'Grape', severity: 'high', treatmentId: 'T009', descriptionKey: 'esca' },
  { id: 13, label: 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', cropName: 'Grape', severity: 'medium', treatmentId: 'T010', descriptionKey: 'leaf_blight' },
  { id: 14, label: 'Grape___healthy', cropName: 'Grape', severity: 'low', treatmentId: 'T000', descriptionKey: 'healthy' },
  { id: 15, label: 'Orange___Haunglongbing_(Citrus_greening)', cropName: 'Orange', severity: 'high', treatmentId: 'T011', descriptionKey: 'citrus_greening' },
  { id: 16, label: 'Peach___Bacterial_spot', cropName: 'Peach', severity: 'medium', treatmentId: 'T012', descriptionKey: 'bacterial_spot' },
  { id: 17, label: 'Peach___healthy', cropName: 'Peach', severity: 'low', treatmentId: 'T000', descriptionKey: 'healthy' },
  { id: 18, label: 'Pepper,_bell___Bacterial_spot', cropName: 'Pepper', severity: 'medium', treatmentId: 'T013', descriptionKey: 'bacterial_spot' },
  { id: 19, label: 'Pepper,_bell___healthy', cropName: 'Pepper', severity: 'low', treatmentId: 'T000', descriptionKey: 'healthy' },
  { id: 20, label: 'Potato___Early_blight', cropName: 'Potato', severity: 'medium', treatmentId: 'T014', descriptionKey: 'early_blight' },
  { id: 21, label: 'Potato___Late_blight', cropName: 'Potato', severity: 'high', treatmentId: 'T015', descriptionKey: 'late_blight' },
  { id: 22, label: 'Potato___healthy', cropName: 'Potato', severity: 'low', treatmentId: 'T000', descriptionKey: 'healthy' },
  { id: 23, label: 'Raspberry___healthy', cropName: 'Raspberry', severity: 'low', treatmentId: 'T000', descriptionKey: 'healthy' },
  { id: 24, label: 'Soybean___healthy', cropName: 'Soybean', severity: 'low', treatmentId: 'T000', descriptionKey: 'healthy' },
  { id: 25, label: 'Squash___Powdery_mildew', cropName: 'Squash', severity: 'medium', treatmentId: 'T016', descriptionKey: 'powdery_mildew' },
  { id: 26, label: 'Strawberry___Leaf_scorch', cropName: 'Strawberry', severity: 'medium', treatmentId: 'T017', descriptionKey: 'leaf_scorch' },
  { id: 27, label: 'Strawberry___healthy', cropName: 'Strawberry', severity: 'low', treatmentId: 'T000', descriptionKey: 'healthy' },
  { id: 28, label: 'Tomato___Bacterial_spot', cropName: 'Tomato', severity: 'medium', treatmentId: 'T018', descriptionKey: 'bacterial_spot' },
  { id: 29, label: 'Tomato___Early_blight', cropName: 'Tomato', severity: 'medium', treatmentId: 'T019', descriptionKey: 'early_blight' },
  { id: 30, label: 'Tomato___Late_blight', cropName: 'Tomato', severity: 'high', treatmentId: 'T020', descriptionKey: 'late_blight' },
  { id: 31, label: 'Tomato___Leaf_Mold', cropName: 'Tomato', severity: 'medium', treatmentId: 'T021', descriptionKey: 'leaf_mold' },
  { id: 32, label: 'Tomato___Septoria_leaf_spot', cropName: 'Tomato', severity: 'medium', treatmentId: 'T022', descriptionKey: 'septoria_leaf_spot' },
  { id: 33, label: 'Tomato___Spider_mites Two-spotted_spider_mite', cropName: 'Tomato', severity: 'high', treatmentId: 'T023', descriptionKey: 'spider_mites' },
  { id: 34, label: 'Tomato___Target_Spot', cropName: 'Tomato', severity: 'medium', treatmentId: 'T024', descriptionKey: 'target_spot' },
  { id: 35, label: 'Tomato___Tomato_Yellow_Leaf_Curl_Virus', cropName: 'Tomato', severity: 'high', treatmentId: 'T025', descriptionKey: 'yellow_leaf_curl' },
  { id: 36, label: 'Tomato___Tomato_mosaic_virus', cropName: 'Tomato', severity: 'high', treatmentId: 'T026', descriptionKey: 'mosaic_virus' },
  { id: 37, label: 'Tomato___healthy', cropName: 'Tomato', severity: 'low', treatmentId: 'T000', descriptionKey: 'healthy' },
];

export const getDiseaseByIndex = (index: number): DiseaseClass =>
  DISEASE_CLASSES[index] ?? DISEASE_CLASSES[37];

export const getDiseaseName = (label: string): string => {
  const parts = label.split('___');
  return parts[1]?.replace(/_/g, ' ') ?? label;
};
