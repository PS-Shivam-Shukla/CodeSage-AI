import { useState } from 'react';
import { RepositoryCard } from '@/components/RepositoryCard';
import { repositoryService } from '@/services/repository.service';

export function RepositoryPage() {
  const [repoPath, setRepoPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleIndex = async () => {
    setError('');
    setSuccess(false);
    setLoading(true);
    try {
      await repositoryService.indexRepository({ repository_path: repoPath });
      setSuccess(true);
    } catch {
      setError('Unable to index the repository. Check the path and backend connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Page header */}
      <div className="mb-stack-lg">
        <h2 className="text-display text-on-surface mb-2">Repository Dashboard</h2>
        <p className="text-body-lg text-on-surface-variant max-w-2xl">
          Index your codebase and manage the vector store from here.
        </p>
      </div>

      <RepositoryCard
        repoPath={repoPath}
        onChange={setRepoPath}
        onSubmit={handleIndex}
        loading={loading}
        success={success}
        error={error}
      />
    </>
  );
}
