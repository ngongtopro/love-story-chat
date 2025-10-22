import { useState } from 'react'
import { Link } from 'react-router-dom'
import { 
  Card, 
  Form, 
  Input, 
  Button, 
  Typography, 
  Space,
  Divider,
  Alert,
  theme
} from 'antd'
import { 
  UserOutlined, 
  LockOutlined,
  CloudOutlined,
  EyeInvisibleOutlined,
  EyeTwoTone
} from '@ant-design/icons'
import { useAuth } from '../../../context/AuthContext'

const { Title, Text } = Typography

interface LoginFormValues {
  username: string
  password: string
}

export default function LoginPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { login } = useAuth()
  const { token } = theme.useToken()
  const [form] = Form.useForm()

  const onFinish = async (values: LoginFormValues) => {
    setLoading(true)
    setError(null)
    try {
      await login(values.username, values.password)
    } catch (err: any) {
      setError(err.message || 'Đăng nhập thất bại')
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
      background: 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)',
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
            <CloudOutlined style={{ fontSize: 48, color: token.colorPrimary }} />
            <Title level={2} style={{ margin: 0, color: token.colorPrimary }}>
              Love Chat
            </Title>
            <Text type="secondary">
              Chào mừng bạn trở lại!
            </Text>
          </Space>
        </div>

        {error && (
          <Alert
            message={error}
            type="error"
            showIcon
            closable
            onClose={() => setError(null)}
            style={{ marginBottom: 24 }}
          />
        )}

        <Form
          form={form}
          name="login"
          onFinish={onFinish}
          layout="vertical"
          size="large"
          autoComplete="off"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: 'Vui lòng nhập tên đăng nhập!' },
              { min: 3, message: 'Tên đăng nhập phải có ít nhất 3 ký tự!' }
            ]}
          >
            <Input 
              prefix={<UserOutlined style={{ color: token.colorTextPlaceholder }} />} 
              placeholder="Tên đăng nhập"
              allowClear
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
              prefix={<LockOutlined style={{ color: token.colorTextPlaceholder }} />} 
              placeholder="Mật khẩu"
              iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
            />
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              block
              loading={loading}
              style={{
                background: 'linear-gradient(90deg, #1890ff, #40a9ff)',
                border: 'none',
                height: 48,
                fontSize: 16
              }}
            >
              Đăng nhập
            </Button>
          </Form.Item>
        </Form>

        <Divider plain>
          <Text type="secondary">Hoặc</Text>
        </Divider>

        <div style={{ textAlign: 'center' }}>
          <Text type="secondary">
            Chưa có tài khoản?{' '}
            <Link to="/register" style={{ color: '#1890ff' }}>
              Đăng ký ngay
            </Link>
          </Text>
        </div>
      </Card>
    </div>
  )
}
