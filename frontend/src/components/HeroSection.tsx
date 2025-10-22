import React, { useEffect, useState } from 'react'
import { Typography, Button, Space, Row, Col } from 'antd'
import { 
  HeartOutlined, 
  RightOutlined,
  MessageOutlined,
  PlayCircleOutlined,
  BugOutlined,
  WalletOutlined
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const { Title, Paragraph } = Typography

const HeroSection: React.FC = () => {
  const navigate = useNavigate()
  const [currentFeature, setCurrentFeature] = useState(0)

  const features = [
    { icon: <MessageOutlined />, text: 'Chat Realtime' },
    { icon: <PlayCircleOutlined />, text: 'Game Online' },
    { icon: <BugOutlined />, text: 'Trang Trại Ảo' },
    { icon: <WalletOutlined />, text: 'Ví Điện Tử' }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % features.length)
    }, 2000)

    return () => clearInterval(interval)
  }, [features.length])

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #ff69b415 0%, #ff149305 100%)',
      display: 'flex',
      alignItems: 'center',
      padding: '0 50px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background Animation */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `
          radial-gradient(circle at 20% 50%, #ff69b410 0%, transparent 50%),
          radial-gradient(circle at 80% 20%, #ff149310 0%, transparent 50%),
          radial-gradient(circle at 40% 80%, #ff69b408 0%, transparent 50%)
        `,
        animation: 'float 6s ease-in-out infinite'
      }} />

      <Row align="middle" style={{ width: '100%', position: 'relative', zIndex: 1 }}>
        <Col xs={24} lg={12}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <div style={{ textAlign: 'center' }}>
              <HeartOutlined style={{ 
                fontSize: 120, 
                color: '#ff69b4',
                marginBottom: 32,
                animation: 'pulse 2s ease-in-out infinite'
              }} />
            </div>
            
            <Title level={1} style={{ 
              fontSize: '4rem',
              fontWeight: 700,
              textAlign: 'center',
              marginBottom: 16,
              background: 'linear-gradient(135deg, #ff69b4 0%, #ff1493 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              animation: 'slideInUp 1s ease-out'
            }}>
              Love Chat
            </Title>
            
            <Title level={3} style={{ 
              textAlign: 'center',
              fontWeight: 400,
              color: '#666',
              marginBottom: 24,
              animation: 'slideInUp 1s ease-out 0.2s both'
            }}>
              Kết nối yêu thương - Chia sẻ niềm vui
            </Title>
            
            <div style={{ 
              textAlign: 'center',
              height: 40,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 32
            }}>
              <Space align="center" size="middle">
                <div style={{
                  fontSize: 24,
                  color: '#ff69b4',
                  transition: 'all 0.5s ease'
                }}>
                  {features[currentFeature].icon}
                </div>
                <Paragraph style={{ 
                  fontSize: 18,
                  margin: 0,
                  color: '#666',
                  fontWeight: 500
                }}>
                  {features[currentFeature].text}
                </Paragraph>
              </Space>
            </div>
            
            <div style={{ textAlign: 'center' }}>
              <Space size="large">
                <Button 
                  type="primary" 
                  size="large"
                  icon={<RightOutlined />}
                  onClick={() => navigate('/register')}
                  style={{ 
                    height: 56,
                    padding: '0 32px',
                    fontSize: 16,
                    borderRadius: 28,
                    background: 'linear-gradient(135deg, #ff69b4 0%, #ff1493 100%)',
                    border: 'none',
                    animation: 'slideInUp 1s ease-out 0.4s both'
                  }}
                >
                  Bắt đầu ngay
                </Button>
                <Button 
                  size="large"
                  onClick={() => navigate('/login')}
                  style={{ 
                    height: 56,
                    padding: '0 32px',
                    fontSize: 16,
                    borderRadius: 28,
                    animation: 'slideInUp 1s ease-out 0.6s both'
                  }}
                >
                  Đăng nhập
                </Button>
              </Space>
            </div>
          </Space>
        </Col>
        
        <Col xs={24} lg={12}>
          <div style={{ 
            textAlign: 'center',
            animation: 'slideInRight 1s ease-out 0.8s both'
          }}>
            <img 
              src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 400'%3E%3Cdefs%3E%3ClinearGradient id='grad1' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' style='stop-color:%23ff69b4;stop-opacity:0.8' /%3E%3Cstop offset='100%25' style='stop-color:%23ff1493;stop-opacity:0.8' /%3E%3C/linearGradient%3E%3C/defs%3E%3Ccircle cx='200' cy='200' r='180' fill='url(%23grad1)' /%3E%3Ccircle cx='160' cy='160' r='20' fill='%23fff' /%3E%3Ccircle cx='240' cy='160' r='20' fill='%23fff' /%3E%3Cpath d='M 150 240 Q 200 280 250 240' stroke='%23fff' stroke-width='8' fill='none' stroke-linecap='round' /%3E%3C/svg%3E"
              alt="Love Chat Character"
              style={{ 
                width: '300px', 
                height: '300px',
                filter: 'drop-shadow(0 20px 40px rgba(255, 105, 180, 0.3))'
              }}
            />
          </div>
        </Col>
      </Row>


    </div>
  )
}

export default HeroSection
