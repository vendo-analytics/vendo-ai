interface StatusIndicatorProps {
    isConnected: boolean
    isConnecting: boolean
  }
  
  export function StatusIndicator({ isConnected, isConnecting }: StatusIndicatorProps) {
    const getStatusConfig = () => {
      if (isConnecting) {
        return {
          dotClass: "bg-yellow-500 animate-[breathe_2s_ease-in-out_infinite]",
          textClass: "text-yellow-600",
          text: "Connecting...",
        }
      } else if (isConnected) {
        return {
          dotClass: "bg-green-500",
          textClass: "text-green-600",
          text: "Connected",
        }
      } else {
        return {
          dotClass: "bg-yellow-500 animate-[breathe_2s_ease-in-out_infinite]",
          textClass: "text-yellow-600",
          text: "Connecting...",
        }
      }
    }
  
    const config = getStatusConfig()
  
    return (
      <>
        <style jsx>{`
          @keyframes breathe {
            0%, 100% { 
              transform: scale(1);
              opacity: 1;
            }
            50% { 
              transform: scale(1.5);
              opacity: 0.7;
            }
          }
        `}</style>
        <div className="flex items-center gap-2 text-sm">
          {/* Status Dot */}
          <div className={`w-2 h-2 rounded-full transition-all duration-300 ${config.dotClass}`} />
  
          {/* Status Text */}
          <span className={`font-medium ${config.textClass}`}>{config.text}</span>
        </div>
      </>
    )
  }
  