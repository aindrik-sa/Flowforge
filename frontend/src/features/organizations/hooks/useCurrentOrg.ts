import { useQuery } from '@tanstack/react-query';
import { organizationsApi } from '../api';
import { useParams } from 'react-router-dom';

export function useCurrentOrg() {
  const { orgId } = useParams<{ orgId: string }>();

  const { data: orgs, isLoading: isLoadingOrgs } = useQuery({
    queryKey: ['organizations'],
    queryFn: organizationsApi.list,
  });

  const currentOrg = orgs?.find((org) => org.id === orgId) || orgs?.[0];

  return {
    orgs: orgs || [],
    currentOrg,
    isLoading: isLoadingOrgs,
  };
}
