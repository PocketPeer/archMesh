"use client";

import NotificationCenter from './NotificationCenter';

interface ClientNotificationCenterProps {
  className?: string;
}

const ClientNotificationCenter: React.FC<ClientNotificationCenterProps> = ({ className }) => {
  return <NotificationCenter className={className} />;
};

export default ClientNotificationCenter;

