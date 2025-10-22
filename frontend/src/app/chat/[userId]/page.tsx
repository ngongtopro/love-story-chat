import ChatPage from '../page'

// This is a wrapper that handles the userId parameter
// The actual ChatPage already handles useParams() to get userId
export default function ChatWithUserPage() {
  return <ChatPage />
}
