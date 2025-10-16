# ArchMesh PoC Frontend

A Next.js 14 frontend application for the ArchMesh PoC, providing a modern interface for AI-powered architecture design.

## Features

- **Project Management**: Create and manage architecture projects
- **Document Upload**: Upload requirements documents in various formats
- **Workflow Tracking**: Monitor AI-powered workflow progress
- **Requirements Review**: Review and approve extracted requirements
- **Architecture Visualization**: View generated system architectures and C4 diagrams
- **Human Review Gates**: Built-in approval points for human oversight

## Tech Stack

- **Next.js 14** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components
- **Sonner** for toast notifications

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`.

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```text
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Landing page
│   └── projects/          # Project management pages
├── components/            # React components
│   └── ui/               # shadcn/ui components
├── lib/                  # Utility libraries
│   ├── api-client.ts     # Backend API client
│   └── utils.ts          # Utility functions
└── types/                # TypeScript type definitions
    └── index.ts          # API and data types
```

## API Integration

The frontend communicates with the ArchMesh backend API through the `api-client.ts` module, which provides:

- Project CRUD operations
- Workflow management
- File upload handling
- Requirements and architecture retrieval
- Human feedback submission

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Usage

1. **Create a Project**: Start by creating a new project with domain selection
2. **Upload Document**: Upload your requirements document (TXT, MD, RST, PDF, DOCX, PPTX)
3. **Monitor Progress**: Track workflow progress through the dashboard
4. **Review Requirements**: Approve or provide feedback on extracted requirements
5. **View Architecture**: Review generated system architecture and C4 diagrams

## Supported File Formats

- **Text Files**: `.txt`, `.md`, `.rst`
- **Documents**: `.pdf`, `.docx`, `.pptx`
- **Size Limit**: 10MB maximum

## Development

The frontend is built with modern React patterns:

- **Server Components** for better performance
- **Client Components** for interactivity
- **TypeScript** for type safety
- **Tailwind CSS** for responsive design
- **shadcn/ui** for consistent UI components

## Contributing

1. Follow the existing code structure
2. Use TypeScript for all new code
3. Follow the established naming conventions
4. Test all new features thoroughly
5. Update documentation as needed
