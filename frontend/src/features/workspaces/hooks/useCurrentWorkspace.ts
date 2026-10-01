import { useQuery } from '@tanstack/react-query';
import { workspacesApi } from '../api';
import { useCurrentOrg } from '../../organizations/hooks/useCurrentOrg';

export function useCurrentWorkspace() {
  const { currentOrg } = useCurrentOrg();
  
  const { data: workspaces, isLoading } = useQuery({
    queryKey: ['workspaces', currentOrg?.id],
    queryFn: () => workspacesApi.list(currentOrg!.id),
    enabled: !!currentOrg,
  });

  // For now, auto-select the first workspace since we don't have a switcher yet.
  const currentWorkspace = workspaces?.[0];

  return {
    workspaces: workspaces || [],
    currentWorkspace,
    isLoading,
  };
}
