import { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Statistic,
  Avatar,
  Typography,
  Space,
  List,
  Spin,
  Badge,
  Divider
} from 'antd'
import {
  UserOutlined,
  MessageOutlined,
  TrophyOutlined,
  PlayCircleOutlined,
  CalendarOutlined
} from '@ant-design/icons'
import { chatAPI, caroAPI } from '../../services/api'
import dayjs from 'dayjs'

const { Title, Text } = Typography

interface User {
  username: string
}

interface MessageStats {
  total_chats: number
  total_messages: number
}

interface GameStats {
  games_won?: number
  total_games?: number
  win_rate?: number
}

interface ProfileData {
  user: User | null
  messageStats: MessageStats
  gameStats: GameStats
  recentMessages: any[]
  recentGames: any[]
}

export default function ProfilePage() {
  const [loading, setLoading] = useState(true)
  const [profileData, setProfileData] = useState<ProfileData>({
    user: null,
    messageStats: { total_chats: 0, total_messages: 0 },
    gameStats: {},
    recentMessages: [],
    recentGames: []
  })

  useEffect(() => {
    loadProfileData()
  }, [])

  const loadProfileData = async () => {
    try {
      setLoading(true)
      
      // Since we don't have a specific profile endpoint, we'll use available APIs
      const [chatsRes] = await Promise.all([
        chatAPI.getPrivateChats().catch(() => ({ data: [] }))
      ])

      // Try to load game stats
      let gameStats = {}
      try {
        const gameRes = await caroAPI.getStats()
        gameStats = gameRes.data
      } catch (error) {
        console.log('Game stats not available')
      }

      setProfileData({
        user: { username: 'Current User' }, // Placeholder
        messageStats: {
          total_chats: Array.isArray(chatsRes.data) ? chatsRes.data.length : 0,
          total_messages: 0 // Would need to count from API
        },
        gameStats,
        recentMessages: [],
        recentGames: []
      })
    } catch (error) {
      console.error('Error loading profile data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '50vh' 
      }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      <Title level={2}>Hồ sơ của tôi</Title>
      
      {/* Profile Header */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={24}>
          <Col xs={24} md={6}>
            <div style={{ textAlign: 'center' }}>
              <Avatar 
                size={120} 
                icon={<UserOutlined />}
                style={{ backgroundColor: '#ff69b4' }}
              />
              <Title level={4} style={{ marginTop: 16, marginBottom: 8 }}>
                {profileData.user?.username || 'Người dùng'}
              </Title>
              <Badge status="success" text="Đang online" />
            </div>
          </Col>
          
          <Col xs={24} md={18}>
            <Row gutter={[16, 16]}>
              <Col xs={12} sm={8}>
                <Statistic
                  title="Tin nhắn đã gửi"
                  value={profileData.messageStats.total_messages || 0}
                  prefix={<MessageOutlined />}
                />
              </Col>
              <Col xs={12} sm={8}>
                <Statistic
                  title="Cuộc trò chuyện"
                  value={profileData.messageStats.total_chats || 0}
                  prefix={<UserOutlined />}
                />
              </Col>
              <Col xs={12} sm={8}>
                <Statistic
                  title="Trận thắng"
                  value={profileData.gameStats.games_won || 0}
                  prefix={<TrophyOutlined />}
                />
              </Col>
              <Col xs={12} sm={8}>
                <Statistic
                  title="Tổng trận đấu"
                  value={profileData.gameStats.total_games || 0}
                  prefix={<PlayCircleOutlined />}
                />
              </Col>
              <Col xs={12} sm={8}>
                <Statistic
                  title="Tỷ lệ thắng"
                  value={profileData.gameStats.win_rate || 0}
                  suffix="%"
                  precision={1}
                  prefix={<TrophyOutlined />}
                />
              </Col>
              <Col xs={12} sm={8}>
                <Statistic
                  title="Ngày tham gia"
                  value={dayjs().format('DD/MM/YYYY')}
                  prefix={<CalendarOutlined />}
                />
              </Col>
            </Row>
          </Col>
        </Row>
      </Card>

      <Row gutter={[16, 16]}>
        {/* Recent Activity */}
        <Col xs={24} lg={12}>
          <Card title="Hoạt động gần đây">
            <List
              dataSource={[
                {
                  type: 'message',
                  title: 'Gửi tin nhắn',
                  description: 'Đã gửi tin nhắn cho người dùng',
                  time: dayjs().subtract(1, 'hour')
                },
                {
                  type: 'game',
                  title: 'Chơi game Caro',
                  description: 'Thắng trận đấu với người chơi khác',
                  time: dayjs().subtract(2, 'hours')
                },
                {
                  type: 'farm',
                  title: 'Thu hoạch cây trồng',
                  description: 'Thu hoạch thành công tại trang trại',
                  time: dayjs().subtract(3, 'hours')
                }
              ]}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      <Avatar 
                        icon={
                          item.type === 'message' ? <MessageOutlined /> :
                          item.type === 'game' ? <TrophyOutlined /> :
                          <UserOutlined />
                        }
                        style={{ 
                          backgroundColor: 
                            item.type === 'message' ? '#1890ff' :
                            item.type === 'game' ? '#52c41a' :
                            '#fa8c16'
                        }}
                      />
                    }
                    title={item.title}
                    description={
                      <Space direction="vertical" size={0}>
                        <Text type="secondary">{item.description}</Text>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {item.time.fromNow()}
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* Achievements */}
        <Col xs={24} lg={12}>
          <Card title="Thành tích">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>🏆 Người chơi mới</Text>
                <br />
                <Text type="secondary">Tham gia Love Chat</Text>
              </div>
              
              <Divider />
              
              <div>
                <Text strong>💬 Người nói chuyện</Text>
                <br />
                <Text type="secondary">Gửi tin nhắn đầu tiên</Text>
              </div>
              
              <Divider />
              
              <div>
                <Text strong>🎮 Người chơi</Text>
                <br />
                <Text type="secondary">Chơi game đầu tiên</Text>
              </div>
              
              <Divider />
              
              <div>
                <Text strong>🌱 Nông dân</Text>
                <br />
                <Text type="secondary">Trồng cây đầu tiên</Text>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  )
}
