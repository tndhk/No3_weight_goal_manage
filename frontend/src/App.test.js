import { render, screen } from '@testing-library/react';
import App from './App';

// モックデータの用意
jest.mock('./services/api', () => ({
  fetchData: jest.fn().mockResolvedValue([]),
  fetchAnalyticsData: jest.fn().mockResolvedValue([]),
}));

// 基本的なレンダリングテスト
test('renders without crashing', () => {
  render(<App />);
  // Navbarのタイトルが表示されていることを確認
  const linkElement = screen.getByText(/React-Flask App/i);
  expect(linkElement).toBeInTheDocument();
});