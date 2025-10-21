import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { 
  Card, 
  Form, 
  Input, 
  Button, 
  Typography, 
  Space,
  Divider 
} from 'antd'
import { 
  UserOutlined, 
  LockOutlined,
  MailOutlined,
  HeartOutlined 
} from '@ant-design/icons'
import { useAuth } from '../context/AuthContext'

const { Title, Text } = Typography

const Register = () => {
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const onFinish = async (values) => {
    setLoading(true)
    try {
      const result = await register({
        username: values.username,
        email: values.email,
        password: values.password,
      })
      
      if (result.success) {
        navigate('/login')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #ff69b4 0%, #ff1493 100%)',
      padding: 20
    }}>
      <Card 
        style={{ 
          width: '100%', 
          maxWidth: 400,
          borderRadius: 16,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)'
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Space direction="vertical" size={8}>
            <HeartOutlined style={{ fontSize: 48, color: '#ff69b4' }} />
            <Title level={2} style={{ margin: 0, color: '#ff69b4' }}>
              Love Chat
            </Title>
            <Text type="secondary">
              Tạo tài khoản mới
            </Text>
          </Space>
        </div>

        <Form
          name="register"
          onFinish={onFinish}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: 'Vui lòng nhập tên đăng nhập!' },
              { min: 3, message: 'Tên đăng nhập phải có ít nhất 3 ký tự!' }
            ]}
          >
            <Input 
              prefix={<UserOutlined />} 
              placeholder="Tên đăng nhập"
            />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Vui lòng nhập email!' },
              { type: 'email', message: 'Email không hợp lệ!' }
            ]}
          >
            <Input 
              prefix={<MailOutlined />} 
              placeholder="Email"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: 'Vui lòng nhập mật khẩu!' },
              { min: 6, message: 'Mật khẩu phải có ít nhất 6 ký tự!' }
            ]}
          >
            <Input.Password 
              prefix={<LockOutlined />} 
              placeholder="Mật khẩu"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            dependencies={['password']}
            rules={[
              { required: true, message: 'Vui lòng xác nhận mật khẩu!' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve()
                  }
                  return Promise.reject(new Error('Mật khẩu xác nhận không khớp!'))
                },
              }),
            ]}
          >
            <Input.Password 
              prefix={<LockOutlined />} 
              placeholder="Xác nhận mật khẩu"
            />
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              block
              loading={loading}
              style={{
                background: 'linear-gradient(90deg, #ff69b4, #ff1493)',
                border: 'none',
                height: 48,
                fontSize: 16
              }}
            >
              Đăng ký
            </Button>
          </Form.Item>
        </Form>

        <Divider plain>
          <Text type="secondary">Hoặc</Text>
        </Divider>

        <div style={{ textAlign: 'center' }}>
          <Text type="secondary">
            Đã có tài khoản?{' '}
            <Link to="/login" style={{ color: '#ff69b4' }}>
              Đăng nhập ngay
            </Link>
          </Text>
        </div>
      </Card>
    </div>
  )
}

export default Register
