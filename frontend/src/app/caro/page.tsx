import { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Button,
  Typography,
  List,
  Modal,
  Form,
  Select,
  message,
  Spin,
  Statistic,
  Badge,
  Space
} from 'antd'
import {
  PlusOutlined,
  PlayCircleOutlined,
  TrophyOutlined
} from '@ant-design/icons'
import { caroAPI } from '../../services/api'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import '../../styles/CaroGame.css'

// Add relativeTime plugin for dayjs
dayjs.extend(relativeTime)

// Interfaces
interface Player {
  id: number
  username: string
}

interface Game {
  id: number
  status: 'waiting' | 'playing' | 'finished'
  player1?: Player
  player2?: Player
  current_player?: Player
  winner?: Player
  board?: string[]
  created_at: string
}

interface GameStats {
  total_games: number
  games_won: number
  win_rate: number
  current_streak: number
}

interface CreateGameData {
  board_size: number
}

const { Title, Text } = Typography
const { Option } = Select

export default function CaroPage() {
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [games, setGames] = useState<Game[]>([])
  const [waitingGames, setWaitingGames] = useState<Game[]>([])
  const [activeGames, setActiveGames] = useState<Game[]>([])
  const [stats, setStats] = useState<GameStats>({} as GameStats)
  const [currentGame, setCurrentGame] = useState<Game | null>(null)
  const [createModalVisible, setCreateModalVisible] = useState(false)
  const [gameModalVisible, setGameModalVisible] = useState(false)

  useEffect(() => {
    loadGameData()
  }, [])

  const loadGameData = async () => {
    try {
      setLoading(true)
      
      // Load all game data
      const [gamesRes, waitingRes, activeRes] = await Promise.all([
        caroAPI.getGames().catch((err) => {
          console.warn('Failed to load games:', err)
          return { data: [] }
        }),
        caroAPI.getWaitingGames().catch((err) => {
          console.warn('Failed to load waiting games:', err)
          return { data: [] }
        }),
        caroAPI.getActiveGames().catch((err) => {
          console.warn('Failed to load active games:', err)
          return { data: [] }
        })
      ])

      console.log('API Responses:', { 
        games: gamesRes.data, 
        waiting: waitingRes.data, 
        active: activeRes.data 
      })

      // Try to load stats
      let gameStats: GameStats = {
        total_games: 0,
        games_won: 0,
        win_rate: 0,
        current_streak: 0
      }
      try {
        const statsRes = await caroAPI.getStats()
        gameStats = statsRes.data
      } catch (error) {
        console.log('Game stats not available')
      }

      setGames(Array.isArray(gamesRes.data) ? gamesRes.data : [])
      setWaitingGames(Array.isArray(waitingRes.data) ? waitingRes.data : [])
      setActiveGames(Array.isArray(activeRes.data) ? activeRes.data : [])
      setStats(gameStats)
    } catch (error) {
      console.error('Error loading game data:', error)
      message.error('Không thể tải dữ liệu game')
    } finally {
      setLoading(false)
    }
  }

  const createGame = async (values: CreateGameData) => {
    try {
      setCreating(true)
      await caroAPI.createGame(values)
      message.success('Tạo game thành công!')
      setCreateModalVisible(false)
      loadGameData()
    } catch (error) {
      console.error('Error creating game:', error)
      message.error('Không thể tạo game')
    } finally {
      setCreating(false)
    }
  }

  const joinGame = async (gameId: number) => {
    try {
      await caroAPI.joinGame(gameId)
      message.success('Tham gia game thành công!')
      loadGameData()
    } catch (error) {
      console.error('Error joining game:', error)
      message.error('Không thể tham gia game')
    }
  }

  const openGameModal = (game: Game) => {
    setCurrentGame(game)
    setGameModalVisible(true)
  }

  const makeMove = async (row: number, col: number) => {
    if (!currentGame) return

    try {
      const response = await caroAPI.makeMove(currentGame.id, row, col)
      setCurrentGame(response.data.game)
      
      if (response.data.move_result.winner) {
        message.success(`Trận đấu kết thúc! Người thắng: ${response.data.move_result.winner}`)
      }
    } catch (error) {
      console.error('Error making move:', error)
      message.error('Không thể thực hiện nước đi')
    }
  }

  const renderBoard = (board: string[]) => {
    if (!board) return null

    const boardSize = Math.sqrt(board.length)
    const boardStyle = {
      gridTemplateColumns: `repeat(${boardSize}, 1fr)`,
      gridTemplateRows: `repeat(${boardSize}, 1fr)`
    }

    return (
      <div className="caro-board" style={boardStyle}>
        {board.map((cell: string, index: number) => {
          const row = Math.floor(index / boardSize)
          const col = index % boardSize
          
          return (
            <button
              key={index}
              className="caro-cell"
              onClick={() => makeMove(row, col)}
              disabled={cell !== '' || currentGame?.status !== 'playing'}
            >
              {cell === 'X' ? '❌' : cell === 'O' ? '⭕' : ''}
            </button>
          )
        })}
      </div>
    )
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
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2}>🎮 Game Caro</Title>
        <Button 
          type="primary" 
          icon={<PlusOutlined />}
          onClick={() => setCreateModalVisible(true)}
        >
          Tạo game mới
        </Button>
      </div>

      {/* Game Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Tổng trận"
              value={stats.total_games || 0}
              prefix={<PlayCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Trận thắng"
              value={stats.games_won || 0}
              prefix={<TrophyOutlined />}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Tỷ lệ thắng"
              value={stats.win_rate || 0}
              suffix="%"
              precision={1}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="Chuỗi thắng"
              value={stats.current_streak || 0}
              prefix={<TrophyOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Waiting Games */}
        <Col xs={24} lg={8}>
          <Card title="Game đang chờ">
            <List
              dataSource={Array.isArray(waitingGames) ? waitingGames : []}
              renderItem={(game) => (
                <List.Item
                  actions={[
                    <Button 
                      type="primary" 
                      size="small"
                      icon={<PlayCircleOutlined />}
                      onClick={() => joinGame(game.id)}
                    >
                      Tham gia
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    avatar={<Badge status="warning" />}
                    title={`Game #${game.id}`}
                    description={
                      <Space direction="vertical" size={0}>
                        <Text>Người tạo: {game.player1?.username}</Text>
                        <Text type="secondary">
                          {dayjs(game.created_at).fromNow()}
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
              locale={{ emptyText: 'Không có game nào đang chờ' }}
            />
          </Card>
        </Col>

        {/* Active Games */}
        <Col xs={24} lg={8}>
          <Card title="Game đang chơi">
            <List
              dataSource={Array.isArray(activeGames) ? activeGames : []}
              renderItem={(game) => (
                <List.Item
                  actions={[
                    <Button 
                      type="primary" 
                      size="small"
                      onClick={() => openGameModal(game)}
                    >
                      Vào game
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    avatar={<Badge status="processing" />}
                    title={`Game #${game.id}`}
                    description={
                      <Space direction="vertical" size={0}>
                        <Text>{game.player1?.username} vs {game.player2?.username}</Text>
                        <Text type="secondary">Lượt: {game.current_player?.username}</Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
              locale={{ emptyText: 'Không có game nào đang chơi' }}
            />
          </Card>
        </Col>

        {/* Game History */}
        <Col xs={24} lg={8}>
          <Card title="Lịch sử game">
            <List
              dataSource={Array.isArray(games) ? games.filter(game => game.status === 'finished').slice(0, 10) : []}
              renderItem={(game) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={
                      <Badge 
                        status={game.winner ? 'success' : 'default'} 
                      />
                    }
                    title={`Game #${game.id}`}
                    description={
                      <Space direction="vertical" size={0}>
                        <Text>
                          {game.player1?.username} vs {game.player2?.username}
                        </Text>
                        {game.winner && (
                          <Text type="success">
                            Thắng: {game.winner.username}
                          </Text>
                        )}
                        <Text type="secondary">
                          {dayjs(game.created_at).fromNow()}
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
              locale={{ emptyText: 'Chưa có lịch sử game' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Create Game Modal */}
      <Modal
        title="Tạo game mới"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        footer={null}
      >
        <Form
          layout="vertical"
          onFinish={createGame}
        >
          <Form.Item
            name="board_size"
            label="Kích thước bàn cờ"
            initialValue={15}
          >
            <Select>
              <Option value={15}>15x15 (Tiêu chuẩn)</Option>
              <Option value={20}>20x20 (Lớn)</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button onClick={() => setCreateModalVisible(false)}>
                Hủy
              </Button>
              <Button type="primary" htmlType="submit" loading={creating}>
                Tạo game
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Game Play Modal */}
      <Modal
        title={
          currentGame ? (
            <Space>
              <Text>Game #{currentGame.id}</Text>
              <Badge 
                status={currentGame.status === 'playing' ? 'processing' : 'success'} 
                text={currentGame.status === 'playing' ? 'Đang chơi' : 'Kết thúc'}
              />
            </Space>
          ) : 'Game'
        }
        open={gameModalVisible}
        onCancel={() => setGameModalVisible(false)}
        footer={null}
        width={600}
      >
        {currentGame && (
          <div style={{ textAlign: 'center' }}>
            <div style={{ marginBottom: 16 }}>
              <Space>
                <Text>
                  {currentGame.player1?.username} vs {currentGame.player2?.username}
                </Text>
                {currentGame.status === 'playing' && (
                  <Text style={{ color: '#1890ff' }}>
                    Lượt: {currentGame.current_player?.username}
                  </Text>
                )}
              </Space>
            </div>
            
            {currentGame.board && renderBoard(currentGame.board)}
            
            {currentGame.winner && (
              <div style={{ marginTop: 16 }}>
                <Text type="success" style={{ fontSize: 18 }}>
                  🎉 Người thắng: {currentGame.winner.username}
                </Text>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}
