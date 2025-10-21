import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Row,
  Col,
  Card,
  List,
  Avatar,
  Input,
  Button,
  Typography,
  Space,
  Badge,
  Spin,
  message,
  Empty
} from 'antd'
import {
  SendOutlined,
  UserOutlined,
  MessageOutlined
} from '@ant-design/icons'
import { chatAPI } from '../services/api'
import dayjs from 'dayjs'

const { TextArea } = Input
const { Title, Text } = Typography

const Chat = () => {
  const { userId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [messageText, setMessageText] = useState('')
  const [users, setUsers] = useState([])
  const [messages, setMessages] = useState([])
  const [currentChat, setCurrentChat] = useState(null)
  const [selectedUser, setSelectedUser] = useState(null)

  useEffect(() => {
    loadUsers()
  }, [])

  useEffect(() => {
    if (userId) {
      selectUser(userId)
    }
  }, [userId])

  const loadUsers = async () => {
    try {
      const response = await chatAPI.getUsers()
      setUsers(response.data)
    } catch (error) {
      console.error('Error loading users:', error)
      message.error('Không thể tải danh sách người dùng')
    } finally {
      setLoading(false)
    }
  }

  const selectUser = async (selectedUserId) => {
    try {
      setLoading(true)
      const user = users.find(u => u.id === parseInt(selectedUserId))
      if (!user) {
        // If users not loaded yet, try to load them first
        await loadUsers()
        const foundUser = users.find(u => u.id === parseInt(selectedUserId))
        if (!foundUser) {
          message.error('Không tìm thấy người dùng')
          return
        }
        setSelectedUser(foundUser)
      } else {
        setSelectedUser(user)
      }

      // Create or get existing chat
      const chatResponse = await chatAPI.createPrivateChat(selectedUserId)
      setCurrentChat(chatResponse.data)

      // Load messages for this chat
      const messagesResponse = await chatAPI.getMessages(chatResponse.data.id)
      setMessages(messagesResponse.data || [])
      
      navigate(`/chat/${selectedUserId}`)
    } catch (error) {
      console.error('Error selecting user:', error)
      message.error('Không thể tải cuộc trò chuyện')
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!messageText.trim() || !currentChat) return

    try {
      setSending(true)
      const response = await chatAPI.sendMessage(currentChat.id, messageText.trim())
      
      // Add new message to the list
      setMessages(prev => [...prev, response.data])
      setMessageText('')
    } catch (error) {
      console.error('Error sending message:', error)
      message.error('Không thể gửi tin nhắn')
    } finally {
      setSending(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
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
    <Row gutter={16} style={{ height: 'calc(100vh - 100px)' }}>
      {/* Users List */}
      <Col xs={24} md={8}>
        <Card 
          title="Danh sách người dùng" 
          style={{ height: '100%' }}
          bodyStyle={{ padding: 0, height: 'calc(100% - 57px)', overflow: 'auto' }}
        >
          <List
            dataSource={users}
            renderItem={(user) => (
              <List.Item
                onClick={() => selectUser(user.id)}
                style={{ 
                  cursor: 'pointer',
                  backgroundColor: selectedUser?.id === user.id ? '#f0f0f0' : 'transparent'
                }}
              >
                <List.Item.Meta
                  avatar={
                    <Badge dot={user.is_online} status={user.is_online ? 'success' : 'default'}>
                      <Avatar icon={<UserOutlined />} />
                    </Badge>
                  }
                  title={user.username}
                  description={user.is_online ? 'Đang online' : 'Offline'}
                />
              </List.Item>
            )}
          />
        </Card>
      </Col>

      {/* Chat Area */}
      <Col xs={24} md={16}>
        <Card 
          title={
            selectedUser ? (
              <Space>
                <Avatar icon={<UserOutlined />} />
                <span>{selectedUser.username}</span>
                <Badge 
                  dot={selectedUser.is_online} 
                  status={selectedUser.is_online ? 'success' : 'default'} 
                />
              </Space>
            ) : (
              'Chọn người dùng để bắt đầu trò chuyện'
            )
          }
          style={{ height: '100%' }}
          bodyStyle={{ 
            padding: 0, 
            height: 'calc(100% - 57px)', 
            display: 'flex', 
            flexDirection: 'column' 
          }}
        >
          {selectedUser ? (
            <>
              {/* Messages Area */}
              <div 
                style={{ 
                  flex: 1, 
                  overflow: 'auto', 
                  padding: 16,
                  backgroundColor: '#fafafa'
                }}
              >
                {messages.length === 0 ? (
                  <Empty 
                    description="Chưa có tin nhắn nào"
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                  />
                ) : (
                  <List
                    dataSource={messages}
                    renderItem={(msg) => (
                      <List.Item style={{ border: 'none', padding: '8px 0' }}>
                        <div style={{ width: '100%' }}>
                          <div style={{
                            display: 'flex',
                            justifyContent: msg.is_own_message ? 'flex-end' : 'flex-start'
                          }}>
                            <div style={{
                              maxWidth: '70%',
                              padding: '8px 12px',
                              borderRadius: 12,
                              backgroundColor: msg.is_own_message ? '#1890ff' : '#ffffff',
                              color: msg.is_own_message ? '#ffffff' : '#000000',
                              border: msg.is_own_message ? 'none' : '1px solid #d9d9d9'
                            }}>
                              <div>{msg.content}</div>
                              <div style={{
                                fontSize: 12,
                                opacity: 0.7,
                                marginTop: 4,
                                textAlign: 'right'
                              }}>
                                {dayjs(msg.timestamp).format('HH:mm')}
                              </div>
                            </div>
                          </div>
                        </div>
                      </List.Item>
                    )}
                  />
                )}
              </div>

              {/* Message Input */}
              <div style={{ 
                padding: 16, 
                borderTop: '1px solid #f0f0f0',
                backgroundColor: '#ffffff'
              }}>
                <Space.Compact style={{ width: '100%' }}>
                  <TextArea
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Nhập tin nhắn..."
                    autoSize={{ minRows: 1, maxRows: 4 }}
                    style={{ flex: 1 }}
                  />
                  <Button
                    type="primary"
                    icon={<SendOutlined />}
                    onClick={sendMessage}
                    loading={sending}
                    disabled={!messageText.trim()}
                  >
                    Gửi
                  </Button>
                </Space.Compact>
              </div>
            </>
          ) : (
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100%',
              flexDirection: 'column'
            }}>
              <MessageOutlined style={{ fontSize: 64, color: '#d9d9d9', marginBottom: 16 }} />
              <Text type="secondary">Chọn một người dùng để bắt đầu trò chuyện</Text>
            </div>
          )}
        </Card>
      </Col>
    </Row>
  )
}

export default Chat
