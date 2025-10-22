import React from 'react'
import { 
  Layout, 
  Button, 
  Typography, 
  Row, 
  Col, 
  Card, 
  Space, 
  Divider,
  Statistic,
  Avatar,
  theme
} from 'antd'
import {
  CloudOutlined,
  MessageOutlined,
  PlayCircleOutlined,
  BugOutlined,
  WalletOutlined,
  UserOutlined,
  TrophyOutlined,
  TeamOutlined,
  SafetyCertificateOutlined,
  ThunderboltOutlined,
  SmileOutlined,
  RightOutlined,
  StarFilled
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import HeroSection from '../components/HeroSection'

const { Header, Content, Footer } = Layout
const { Title, Paragraph, Text } = Typography

const LandingPage: React.FC = () => {
  const navigate = useNavigate()
  const { token } = theme.useToken()

  const features = [
    {
      icon: <MessageOutlined style={{ fontSize: 24, color: token.colorPrimary }} />,
      title: 'Chat Realtime',
      description: 'Trò chuyện trực tuyến với bạn bè một cách nhanh chóng và an toàn'
    },
    {
      icon: <PlayCircleOutlined style={{ fontSize: 24, color: '#40a9ff' }} />,
      title: 'Game Online',
      description: 'Chơi game Caro và nhiều trò chơi khác cùng người thân yêu'
    },
    {
      icon: <BugOutlined style={{ fontSize: 24, color: '#1890ff' }} />,
      title: 'Trang Trại Ảo',
      description: 'Xây dựng và quản lý trang trại của riêng bạn'
    },
    {
      icon: <WalletOutlined style={{ fontSize: 24, color: '#40a9ff' }} />,
      title: 'Ví Điện Tử',
      description: 'Quản lý tài chính cá nhân một cách dễ dàng và tiện lợi'
    }
  ]

  const stats = [
    { title: 'Người dùng hoạt động', value: 1000, suffix: '+' },
    { title: 'Tin nhắn mỗi ngày', value: 50000, suffix: '+' },
    { title: 'Trận game đã chơi', value: 25000, suffix: '+' },
    { title: 'Đánh giá 5 sao', value: 4.8, precision: 1, suffix: '/5' }
  ]

  const testimonials = [
    {
      avatar: <UserOutlined />,
      name: 'Nguyễn Văn A',
      comment: 'Ứng dụng rất tuyệt vời! Tôi có thể trò chuyện và chơi game với bạn bè mọi lúc.'
    },
    {
      avatar: <UserOutlined />,
      name: 'Trần Thị B',
      comment: 'Giao diện đẹp, dễ sử dụng. Đặc biệt thích tính năng trang trại ảo.'
    },
    {
      avatar: <UserOutlined />,
      name: 'Lê Minh C',
      comment: 'Ví điện tử rất tiện lợi, giúp tôi quản lý chi tiêu hiệu quả hơn.'
    }
  ]

  return (
    <Layout className="landing-page">
      {/* Header */}
      <Header style={{ 
        background: 'rgba(255, 255, 255, 0.95)', 
        backdropFilter: 'blur(10px)',
        position: 'fixed',
        top: 0,
        width: '100%',
        zIndex: 1000,
        borderBottom: '1px solid #f0f0f0',
        padding: '0 50px'
      }}>
        <Row justify="space-between" align="middle" style={{ height: '100%' }}>
          <Col>
            <Space align="center">
              <CloudOutlined style={{ fontSize: 32, color: token.colorPrimary }} />
              <Title level={3} style={{ margin: 0, color: token.colorPrimary }}>
                Love Chat
              </Title>
            </Space>
          </Col>
          <Col>
            <Space size="large">
              <Button type="text" size="large">Tính năng</Button>
              <Button type="text" size="large">Về chúng tôi</Button>
              <Button type="text" size="large">Liên hệ</Button>
              <Button 
                type="primary" 
                size="large"
                onClick={() => navigate('/login')}
              >
                Đăng nhập
              </Button>
            </Space>
          </Col>
        </Row>
      </Header>

      <Content style={{ marginTop: 64 }}>
        {/* Hero Section */}
        <HeroSection />

        {/* Statistics */}
        <div style={{ padding: '80px 50px', background: '#fff' }}>
          <Row gutter={[32, 32]} justify="center">
            {stats.map((stat, index) => (
              <Col key={index} xs={12} md={6}>
                <Card 
                  bordered={false}
                  style={{ textAlign: 'center', height: '100%' }}
                  bodyStyle={{ padding: '32px 16px' }}
                >
                  <Statistic
                    title={stat.title}
                    value={stat.value}
                    precision={stat.precision}
                    suffix={stat.suffix}
                    valueStyle={{ 
                      color: token.colorPrimary,
                      fontSize: '2rem',
                      fontWeight: 'bold'
                    }}
                  />
                </Card>
              </Col>
            ))}
          </Row>
        </div>

        {/* Features */}
        <div style={{ 
          padding: '80px 50px',
          background: `linear-gradient(180deg, #fff 0%, ${token.colorBgLayout} 100%)`
        }}>
          <Row justify="center" style={{ marginBottom: 60 }}>
            <Col xs={24} md={16} style={{ textAlign: 'center' }}>
              <Title level={2}>Tính năng nổi bật</Title>
              <Paragraph style={{ fontSize: 16, color: token.colorTextSecondary }}>
                Khám phá những tính năng độc đáo và thú vị của Love Chat
              </Paragraph>
            </Col>
          </Row>
          
          <Row gutter={[32, 32]} justify="center">
            {features.map((feature, index) => (
              <Col key={index} xs={24} sm={12} md={6}>
                <Card
                  hoverable
                  style={{ 
                    height: '100%',
                    borderRadius: 16,
                    border: `1px solid ${token.colorBorder}`
                  }}
                  bodyStyle={{ 
                    padding: '32px 24px',
                    textAlign: 'center'
                  }}
                >
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    <div style={{ 
                      width: 64,
                      height: 64,
                      borderRadius: '50%',
                      background: `${token.colorPrimary}10`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      margin: '0 auto'
                    }}>
                      {feature.icon}
                    </div>
                    <Title level={4} style={{ margin: 0 }}>
                      {feature.title}
                    </Title>
                    <Paragraph style={{ 
                      margin: 0,
                      color: token.colorTextSecondary 
                    }}>
                      {feature.description}
                    </Paragraph>
                  </Space>
                </Card>
              </Col>
            ))}
          </Row>
        </div>

        {/* Testimonials */}
        <div style={{ padding: '80px 50px', background: '#fff' }}>
          <Row justify="center" style={{ marginBottom: 60 }}>
            <Col xs={24} md={16} style={{ textAlign: 'center' }}>
              <Title level={2}>Người dùng nói gì</Title>
              <Paragraph style={{ fontSize: 16, color: token.colorTextSecondary }}>
                Cảm nhận từ những người dùng thực sự của Love Chat
              </Paragraph>
            </Col>
          </Row>
          
          <Row gutter={[32, 32]} justify="center">
            {testimonials.map((testimonial, index) => (
              <Col key={index} xs={24} md={8}>
                <Card
                  style={{ 
                    height: '100%',
                    borderRadius: 16
                  }}
                  bodyStyle={{ padding: '32px 24px' }}
                >
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    <div style={{ textAlign: 'center' }}>
                      <Space direction="vertical" size="small">
                        <Avatar size={64} icon={testimonial.avatar} />
                        <Text strong>{testimonial.name}</Text>
                        <div>
                          {[...Array(5)].map((_, i) => (
                            <StarFilled 
                              key={i}
                              style={{ 
                                color: '#fadb14',
                                fontSize: 16,
                                marginRight: 2
                              }} 
                            />
                          ))}
                        </div>
                      </Space>
                    </div>
                    <Paragraph style={{ 
                      textAlign: 'center',
                      fontStyle: 'italic',
                      margin: 0,
                      color: token.colorTextSecondary
                    }}>
                      "{testimonial.comment}"
                    </Paragraph>
                  </Space>
                </Card>
              </Col>
            ))}
          </Row>
        </div>

        {/* CTA Section */}
        <div style={{
          background: `linear-gradient(135deg, ${token.colorPrimary} 0%, #40a9ff 100%)`,
          padding: '80px 50px',
          textAlign: 'center',
          color: '#fff'
        }}>
          <Row justify="center">
            <Col xs={24} md={16}>
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <Title level={2} style={{ color: '#fff', margin: 0 }}>
                  Sẵn sàng bắt đầu chưa?
                </Title>
                <Paragraph style={{ 
                  fontSize: 18,
                  color: 'rgba(255, 255, 255, 0.9)',
                  margin: 0
                }}>
                  Tham gia cộng đồng Love Chat ngay hôm nay và khám phá thế giới kết nối mới!
                </Paragraph>
                <div>
                  <Button 
                    type="primary"
                    size="large"
                    ghost
                    icon={<RightOutlined />}
                    onClick={() => navigate('/register')}
                    style={{ 
                      height: 56,
                      padding: '0 32px',
                      fontSize: 16,
                      borderRadius: 28,
                      borderColor: '#fff',
                      color: '#fff'
                    }}
                  >
                    Đăng ký miễn phí
                  </Button>
                </div>
              </Space>
            </Col>
          </Row>
        </div>
      </Content>

      {/* Footer */}
      <Footer style={{ 
        background: '#001529',
        color: '#fff',
        padding: '40px 50px 20px'
      }}>
        <Row gutter={[32, 32]}>
          <Col xs={24} md={8}>
            <Space direction="vertical" size="middle">
              <Space align="center">
                <CloudOutlined style={{ fontSize: 24, color: token.colorPrimary }} />
                <Text strong style={{ color: '#fff', fontSize: 18 }}>
                  Love Chat
                </Text>
              </Space>
              <Paragraph style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Nền tảng kết nối yêu thương, tạo ra những trải nghiệm tuyệt vời cho người dùng.
              </Paragraph>
            </Space>
          </Col>
          <Col xs={24} md={8}>
            <Space direction="vertical" size="middle">
              <Text strong style={{ color: '#fff' }}>Liên kết nhanh</Text>
              <Space direction="vertical">
                <Button type="link" style={{ color: 'rgba(255, 255, 255, 0.7)', padding: 0 }}>
                  Trang chủ
                </Button>
                <Button type="link" style={{ color: 'rgba(255, 255, 255, 0.7)', padding: 0 }}>
                  Tính năng
                </Button>
                <Button type="link" style={{ color: 'rgba(255, 255, 255, 0.7)', padding: 0 }}>
                  Về chúng tôi
                </Button>
              </Space>
            </Space>
          </Col>
          <Col xs={24} md={8}>
            <Space direction="vertical" size="middle">
              <Text strong style={{ color: '#fff' }}>Liên hệ</Text>
              <Space direction="vertical">
                <Text style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  Email: hello@lovechat.com
                </Text>
                <Text style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  Hotline: 1900 xxxx
                </Text>
              </Space>
            </Space>
          </Col>
        </Row>
        
        <Divider style={{ borderColor: 'rgba(255, 255, 255, 0.2)' }} />
        
        <div style={{ textAlign: 'center' }}>
          <Text style={{ color: 'rgba(255, 255, 255, 0.5)' }}>
            © 2024 Love Chat. All rights reserved.
          </Text>
        </div>
      </Footer>
    </Layout>
  )
}

export default LandingPage
