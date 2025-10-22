# App Router Structure

Cấu trúc frontend mới được tổ chức theo pattern của Next.js App Router, giúp dễ dàng quản lý và mở rộng.

## 📁 Cấu trúc thư mục

```
src/
  app/                     # App router (Next.js style)
    layout.tsx            # Layout tổng cho tất cả authenticated pages
    page.tsx              # Home page (/)
    routes.tsx            # Router configuration
    
    chat/                 # Chat module
      page.tsx           # Chat list (/chat)
      [userId]/          # Dynamic route
        page.tsx         # Chat with specific user (/chat/:userId)
    
    profile/              # Profile module  
      page.tsx           # Profile page (/profile)
    
    caro/                 # Caro game module
      page.tsx           # Caro game page (/caro)
    
    farm/                 # Farm module
      page.tsx           # Farm page (/farm)
    
    wallet/               # Wallet module
      page.tsx           # Wallet page (/wallet)
    
    auth/                 # Authentication module
      login/
        page.tsx         # Login page (/auth/login)
      register/
        page.tsx         # Register page (/auth/register)
```

## 🔗 URL Mapping

### Authentication Routes (No Layout)
- `/` → LandingPage
- `/auth/login` → Login
- `/auth/register` → Register

### App Routes (With Layout)
- `/` → Home (authenticated)
- `/chat` → Chat list
- `/chat/:userId` → Chat with specific user
- `/profile` → User profile
- `/caro` → Caro game
- `/farm` → Farm simulation
- `/wallet` → Wallet management

## 🏗️ Architecture Benefits

1. **Clear Separation**: Mỗi feature có folder riêng
2. **Consistent Naming**: Tất cả đều dùng `page.tsx`
3. **Easy Navigation**: URL structure rõ ràng và logic
4. **Scalable**: Dễ thêm mới features và nested routes
5. **Layout Management**: Layout tự động apply cho authenticated routes

## 🔄 Migration Status: COMPLETE ✅

Migration đã hoàn tất! Tất cả components đã được chuyển từ `/pages` sang `/app` structure:
- ✅ Removed old `/pages` folder completely
- ✅ Moved CSS files to `/src/styles/` for better organization  
- ✅ All functionality preserved with TypeScript safety
- ✅ No breaking changes to existing features

## 🚀 Future Enhancements

- [ ] Lazy loading cho từng module
- [ ] Nested layouts cho từng section
- [ ] Route guards và permissions
- [ ] SEO metadata cho từng page
- [ ] Error boundaries cho từng module
